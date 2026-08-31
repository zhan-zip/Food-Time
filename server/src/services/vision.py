"""外部服务 - Qwen VL 视觉模型客户端（简版骨架，遗留）

正式的多模态识别客户端在 services/qwen.py（qwen_vl，含 OCR 记账、
食材识别、防 SSRF 的 is_safe_image_url 等）；本模块仅为早期极简壳，
实际功能请使用 qwen_vl。
"""

from src.config import settings


class VisionClient:
    def __init__(self):
        self.api_key = settings.QWEN_API_KEY
        self.base_url = settings.QWEN_BASE_URL
        self.model = settings.QWEN_MODEL

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key != "sk-your-qwen-key")


vision = VisionClient()
