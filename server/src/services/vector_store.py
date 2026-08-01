"""向量存储 — chromadb RAG 检索

负责：
1. 启动时对所有食物数据向量化并存入 chromadb
2. 收到用户消息时自动进行检索（优先向量，回退关键词）
3. 支持手动触发搜索
"""

import json
import chromadb
from chromadb.config import Settings as ChromaSettings

CHROMA_PATH = "./chroma_data"
COLLECTION_NAME = "foods"

# 维度和距离函数（text-embedding-v3 输出 1024 维）
EMBEDDING_DIM = 1024
DISTANCE_FN = "cosine"


class VectorStore:
    """chromadb 包装器 + 中文关键词回退"""

    def __init__(self):
        self._client = chromadb.PersistentClient(
            path=CHROMA_PATH,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = None
        self._keyword_index: list[dict] = []  # 内存中的关键词索引

    @property
    def collection(self):
        if self._collection is None:
            self._collection = self._client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": DISTANCE_FN},
            )
        return self._collection

    @property
    def is_ready(self) -> bool:
        """是否已有索引数据"""
        return len(self._keyword_index) > 0 or (
            self.collection.count() > 0
        )

    # ===========================================================
    # 索引构建（启动时调用一次）
    # ===========================================================
    async def build_index(self, foods: list[dict], embed_func):
        """对所有食物构建关键词索引 + 向量索引"""
        if not foods:
            print("[VectorStore] 无食物数据，跳过索引构建")
            return

        # 1. 构建内存关键词索引（始终可用）
        self._keyword_index = []
        for f in foods:
            doc = self._food_to_text(f)
            # 提取所有关键词（中文逐字 + 完整词）
            name = f.get("name", "")
            cuisine = f.get("cuisine", "")
            cat_name = f.get("category_name", "")
            keywords = set()
            # 食物名逐字
            for ch in name:
                if '\u4e00' <= ch <= '\u9fff':
                    keywords.add(ch)
            # 完整食物名
            keywords.add(name)
            # 菜系
            if cuisine:
                keywords.add(cuisine)
            # 分类
            if cat_name:
                keywords.add(cat_name)
            # 标签
            tags = f.get("tags", "")
            if isinstance(tags, str):
                try:
                    tags = json.loads(tags)
                except Exception:
                    tags = {}
            if isinstance(tags, dict):
                for v in tags.values():
                    if isinstance(v, str):
                        keywords.add(v)

            self._keyword_index.append({
                "id": str(f["id"]),
                "name": name,
                "keywords": keywords,
                "document": doc,
                "metadata": {
                    "name": name,
                    "cuisine": cuisine,
                    "category_id": str(f.get("category_id", "")),
                    "calories": str(f.get("calories_per_100g", "")),
                },
            })

        print(f"[VectorStore] 关键词索引构建完成，共 {len(self._keyword_index)} 条")

        # 2. 构建向量索引（耗时，仅当 embedding 可用）
        try:
            self._client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": DISTANCE_FN},
        )

        batch_size = 50
        embedding_ok = True
        for i in range(0, len(foods), batch_size):
            batch = foods[i : i + batch_size]
            ids = [str(f["id"]) for f in batch]
            documents = [self._food_to_text(f) for f in batch]
            metadatas = [
                {
                    "name": f["name"],
                    "cuisine": f.get("cuisine", ""),
                    "category_id": str(f.get("category_id", "")),
                    "calories": str(f.get("calories_per_100g", "")),
                }
                for f in batch
            ]

            if embedding_ok:
                try:
                    embeddings = await embed_func(documents)
                except Exception:
                    embedding_ok = False
                    embeddings = [[0.0] * EMBEDDING_DIM for _ in batch]

            try:
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas,
                    embeddings=embeddings,
                )
            except Exception as e:
                print(f"[VectorStore] 向量写入失败: {e}")

        print(f"[VectorStore] 向量索引构建完成，共 {self.collection.count()} 条，embedding={'OK' if embedding_ok else '未启用'}")

    # ===========================================================
    # 检索：优先向量，回退关键词
    # ===========================================================
    async def search(self, query: str, embed_func, n_results: int = 3) -> list[dict]:
        """检索食物，向量优先，失败回退关键词"""
        # 先试向量检索
        if self.collection.count() > 0:
            try:
                query_embedding = await embed_func([query])
                results = self.collection.query(
                    query_embeddings=query_embedding,
                    n_results=n_results,
                    include=["documents", "metadatas", "distances"],
                )
                if results["ids"] and results["ids"][0]:
                    items = []
                    for j in range(len(results["ids"][0])):
                        items.append({
                            "id": results["ids"][0][j],
                            "document": results["documents"][0][j] if results["documents"] else "",
                            "metadata": results["metadatas"][0][j] if results["metadatas"] else {},
                        })
                    return items
            except Exception:
                pass  # 回退到关键词

        # 关键词检索回退
        return self._search_keywords(query, n_results)

    def _search_keywords(self, query: str, n: int) -> list[dict]:
        """基于中文关键词的检索（始终可用，无需API）"""
        if not self._keyword_index:
            return []

        # 提取查询中的关键词
        q_keywords = set()
        for ch in query:
            if '\u4e00' <= ch <= '\u9fff':
                q_keywords.add(ch)

        scored = []
        for item in self._keyword_index:
            item_kw = item["keywords"]
            # 命中分数 = Jaccard 相似度
            if not q_keywords:
                score = 0
            else:
                intersection = q_keywords & item_kw
                union = q_keywords | item_kw
                score = len(intersection) / len(union) if union else 0

            # 完整词匹配加分
            name = item["name"]
            for kw in q_keywords:
                if kw in name:
                    score += 0.2

            if score > 0:
                scored.append((score, item))

        scored.sort(key=lambda x: x[0], reverse=True)

        return [
            {"id": item["id"], "document": item["document"], "metadata": item["metadata"]}
            for _, item in scored[:n]
        ]

    # ===========================================================
    # 工具
    # ===========================================================
    @staticmethod
    def _food_to_text(food: dict) -> str:
        """食物字典 → 待索引文本"""
        parts = [food["name"]]
        if food.get("cuisine"):
            parts.append(f"菜系:{food['cuisine']}")
        if food.get("category_name"):
            parts.append(f"分类:{food['category_name']}")
        if food.get("calories_per_100g"):
            parts.append(f"热量:{food['calories_per_100g']}kcal/100g")
        if food.get("tags"):
            tags = food["tags"]
            if isinstance(tags, str):
                tags = json.loads(tags)
            if isinstance(tags, list):
                parts.append("标签:" + ",".join(tags))
        return " | ".join(parts)


vector_store = VectorStore()
