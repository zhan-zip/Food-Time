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

    async def parse_receipt(self, image_url: str) -> tuple[dict | None, str | None]:
        """识别小票/账单图片，提取金额和分类。返回 (result_dict, error_msg)"""
        if not self.is_configured:
            return None, "Qwen VL 未配置"

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
                                "你是一个饮食消费记账助手。请分析这张账单/小票/支付截图中的消费信息，"
                                "以JSON格式返回：\n"
                                '{"amount": 金额数字, "category": "分类", "description": "简要描述"}\n\n'
                                "分类只能是以下之一: food(餐饮), delivery(外卖), snack(零食), drink(饮品), grocery(食材采购)\n"
                                "如果无法识别，amount返回0。description用中文简要描述（不超过20字）。"
                                "只返回JSON，不要包含其他文字。"
                            ),
                        },
                    ],
                }],
                max_tokens=300,
                temperature=0.1,
            )
            content = resp.choices[0].message.content or ""
            # 尝试解析 JSON（可能被包裹在 markdown 代码块中）
            import json
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # 尝试从 markdown 代码块或纯文本中提取 JSON
                import re
                match = re.search(r'\{[\s\S]*\}', content)
                if match:
                    result = json.loads(match.group(0))
                else:
                    return None, "无法解析 AI 返回内容"
            return result, None
        except Exception as e:
            return None, str(e)


qwen_vl = QwenVLClient()
