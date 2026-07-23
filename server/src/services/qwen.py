"""Qwen VL API 客户端 — 多模态图片识别"""

from openai import AsyncOpenAI
from src.config import settings


class QwenVLClient:
    """Qwen VL 图片分析客户端"""

    def __init__(self):
        self.api_key = settings.QWEN_API_KEY
        self.base_url = settings.QWEN_BASE_URL
        self.model = settings.QWEN_MODEL
        self._client: AsyncOpenAI | None = None

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key not in ("sk-your-qwen-key", ""))

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
        return self._client

    async def analyze_food(self, image_url: str) -> str | None:
        """分析食物图片，识别种类并估算营养"""
        if not self.is_configured:
            return None

        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url},
                        },
                        {
                            "type": "text",
                            "text": (
                                "请识别图片中的食物，按以下格式回答：\n"
                                "1. 食物名称\n"
                                "2. 主要食材（列出2-5种）\n"
                                "3. 估算营养（热量kcal、蛋白质g、脂肪g、碳水g，以每100g计）\n"
                                "4. 菜系归属\n"
                                "5. 一句话点评\n\n"
                                "如果无法确定图片是食物，说明原因。"
                            ),
                        },
                    ],
                }],
                max_tokens=500,
                temperature=0.3,
            )
            return resp.choices[0].message.content
        except Exception as e:
            print(f"[QwenVL] 识别失败: {e}")
            return None


qwen_vl = QwenVLClient()
