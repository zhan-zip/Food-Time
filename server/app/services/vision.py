"""外部服务 - Qwen VL 视觉模型客户端（骨架）"""

from app.config import settings


class VisionClient:
    def __init__(self):
        self.api_key = settings.QWEN_API_KEY
        self.base_url = settings.QWEN_BASE_URL
        self.model = settings.QWEN_MODEL

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key != "sk-your-qwen-key")


vision = VisionClient()
