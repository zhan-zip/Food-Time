"""向量存储 — chromadb RAG 检索

负责：
1. 启动时对所有食物数据向量化并存入 chromadb
2. 收到用户消息时自动进行语义检索
3. 支持手动触发搜索
"""

import json
import chromadb
from chromadb.config import Settings as ChromaSettings

CHROMA_PATH = "./chroma_data"
COLLECTION_NAME = "foods"

# 维度和距离函数
EMBEDDING_DIM = 1536
DISTANCE_FN = "cosine"


class VectorStore:
    """chromadb 包装器"""

    def __init__(self):
        self._client = chromadb.PersistentClient(
            path=CHROMA_PATH,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = None

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
        try:
            return self.collection.count() > 0
        except Exception:
            return False

    # ===========================================================
    # 索引构建（启动时调用一次）
    # ===========================================================
    async def build_index(self, foods: list[dict], embed_func):
        """对所有食物重新构建向量索引"""
        if not foods:
            print("[VectorStore] 无食物数据，跳过索引构建")
            return

        # 清空旧索引
        try:
            self._client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": DISTANCE_FN},
        )

        batch_size = 50
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

            try:
                embeddings = await embed_func(documents)
            except Exception:
                embeddings = [[0.0] * EMBEDDING_DIM for _ in batch]

            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings,
            )

        print(f"[VectorStore] 索引构建完成，共 {self.collection.count()} 条")

    # ===========================================================
    # 检索
    # ===========================================================
    async def search(self, query: str, embed_func, n_results: int = 3) -> list[dict]:
        """语义搜索食物，返回 top-k 结果"""
        if not self.is_ready:
            return []

        try:
            query_embedding = await embed_func([query])
        except Exception:
            return []

        try:
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )
        except Exception:
            return []

        items = []
        if results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                items.append({
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i] if results["documents"] else "",
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0,
                })
        return items

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
