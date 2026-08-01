"""DeepSeek API 客户端 — 对话 + Embedding

对应 qq-agent 的 llm/llm.py
"""

from openai import AsyncOpenAI
import httpx
from src.config import settings


class DeepSeekClient:
    """DeepSeek API 封装：支持 chat_with_tools + embed"""

    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.model = settings.DEEPSEEK_MODEL
        # DeepSeek 官方不提供 embedding 端点，向量化复用 Qwen/DashScope text-embedding-v3
        self.embed_model = "text-embedding-v3"
        self._client: AsyncOpenAI | None = None
        self._embed_client: AsyncOpenAI | None = None

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key not in ("sk-your-deepseek-key", ""))

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            # 修复 H8：显式设置超时，避免 openai 库默认 600s 导致 API 挂起时阻塞 10 分钟
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=10.0),
            )
        return self._client

    @property
    def embed_client(self) -> AsyncOpenAI:
        """向量化客户端：基于 Qwen/DashScope（DeepSeek 无 embedding 端点）"""
        if self._embed_client is None:
            self._embed_client = AsyncOpenAI(
                api_key=settings.QWEN_API_KEY,
                base_url=settings.QWEN_BASE_URL,
                timeout=httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=10.0),
            )
        return self._embed_client

    # ===========================================================
    # 对话 — 带工具调用（非流式，第一轮）
    # ===========================================================
    async def chat_with_tools(self, messages: list[dict], tools: list[dict]) -> dict | None:
        """调用 DeepSeek，允许 tool_calls。返回 message 对象或 None"""
        if not self.is_configured:
            return None
        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                stream=False,
                temperature=0.7,
                max_tokens=2048,
            )
            return resp.choices[0].message
        except Exception as e:
            print(f"[DeepSeek] chat_with_tools 失败: {e}")
            return None

    # ===========================================================
    # 对话 — 流式（第二轮，拿到工具结果后）
    # ===========================================================
    async def chat_stream(self, messages: list[dict]):
        """流式对话，yield 每个 delta chunk"""
        if not self.is_configured:
            yield ""
            return
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=0.7,
                max_tokens=2048,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
        except Exception as e:
            print(f"[DeepSeek] chat_stream 失败: {e}")
            yield ""

    # ===========================================================
    # 普通对话（无工具，降级用）
    # ===========================================================
    async def chat_simple(self, messages: list[dict]) -> str | None:
        """无工具调用，直接返回文本"""
        if not self.is_configured:
            return None
        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False,
                temperature=0.7,
                max_tokens=1024,
            )
            return resp.choices[0].message.content
        except Exception as e:
            print(f"[DeepSeek] chat_simple 失败: {e}")
            return None

    # ===========================================================
    # Embedding — 用于 chromadb RAG 检索
    # ===========================================================
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """将文本转为向量。使用 Qwen/DashScope text-embedding-v3（复用 QWEN_API_KEY）。

        DeepSeek 官方不提供 embedding 端点，原实现用 deepseek-chat 调 /embeddings 必然失败，
        导致 ChromaDB 全为零向量、语义检索无效（C1）。现改为 DashScope 的 text-embedding-v3，
        失败时返回 1024 维零向量，由 vector_store 的关键词回退兜底。
        """
        if not settings.QWEN_API_KEY or settings.QWEN_API_KEY in ("sk-your-qwen-key", ""):
            print("[Embed] QWEN_API_KEY 未配置，使用零向量 fallback")
            return [[0.0] * 1024 for _ in texts]
        try:
            # DashScope text-embedding-v3 单次请求最多 10 条，内部自动分批
            results: list[list[float]] = []
            for i in range(0, len(texts), 10):
                batch = texts[i:i + 10]
                resp = await self.embed_client.embeddings.create(
                    model=self.embed_model,
                    input=batch,
                )
                results.extend([d.embedding for d in resp.data])
            return results
        except Exception as e:
            print(f"[Embed] DashScope embedding 失败: {e}")
            return [[0.0] * 1024 for _ in texts]


deepseek = DeepSeekClient()
