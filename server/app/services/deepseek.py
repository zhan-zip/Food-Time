"""外部服务 - DeepSeek API 客户端（骨架）"""

from app.config import settings


class DeepSeekClient:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.model = settings.DEEPSEEK_MODEL

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key != "sk-your-deepseek-key")


deepseek = DeepSeekClient()
