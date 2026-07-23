"""DeepSeek API 客户端 — 对话 + Embedding

对应 qq-agent 的 llm/llm.py
"""

from openai import AsyncOpenAI
from src.config import settings


class DeepSeekClient:
    """DeepSeek API 封装：支持 chat_with_tools + embed"""

    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.model = settings.DEEPSEEK_MODEL
        self.embed_model = "deepseek-chat"  # DeepSeek 暂无专用 embedding，用 chat 模型 proxy
        self._client: AsyncOpenAI | None = None

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key not in ("sk-your-deepseek-key", ""))

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
        return self._client

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
        """将文本转为向量。用 /embeddings 端点"""
        if not self.is_configured:
            # fallback：返回零向量（维度 1536）
            return [[0.0] * 1536 for _ in texts]
        try:
            resp = await self.client.embeddings.create(
                model="deepseek-chat",  # DeepSeek 不提供专用 embedding，回退
                input=texts,
            )
            return [d.embedding for d in resp.data]
        except Exception:
            # embedding 不可用时返回零向量
            print("[DeepSeek] embed 不可用，使用零向量 fallback")
            return [[0.0] * 1536 for _ in texts]


deepseek = DeepSeekClient()
