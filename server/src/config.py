"""应用配置 - 从 .env 读取"""

from pydantic_settings import BaseSettings
from typing import List


# 已知不安全的开发默认值（历史遗留），用于启动安全校验
INSECURE_LEGACY_VALUES = {
    "JWT_SECRET": "food-time-dev-secret",
    "ADMIN_PASSWORD": "admin123",
}


class Settings(BaseSettings):
    # 数据库
    DATABASE_URL: str = "mysql+aiomysql://root:123456@localhost:3307/food_time"

    # JWT（默认置空，启动时强制校验，禁止使用不安全默认值）
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080  # 7 天

    # DeepSeek
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # Qwen VL
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_MODEL: str = "qwen-vl-max"

    # Pixabay 图片服务（Key 仅存 .env，不暴露前端）
    PIXABAY_API_KEY: str = ""

    # 通义万相（AI 生成菜谱图片，Key 仅存 .env）
    IMG_GEN_API_KEY: str = ""
    IMG_GEN_BASE_URL: str = ""
    IMG_GEN_MODEL: str = "kwai-kolors/kolors"

    # 邮件
    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@food-time.com"

    # 高德地图 Web 服务（附近美食 POI 搜索，复用前端定位 Key）
    AMAP_KEY: str = ""

    # Tavily 联网搜索（AI 实时搜索，https://tavily.com 免费申请）
    TAVILY_API_KEY: str = ""

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    # 管理员（默认置空，启动时强制校验，禁止使用不安全默认值）
    ADMIN_EMAIL: str = "admin@food-time.com"
    ADMIN_PASSWORD: str = ""

    # 调试
    DEBUG: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()


def check_security_config(cfg: Settings) -> list[str]:
    """启动安全校验：检查 JWT 密钥与管理密码是否为空或仍使用已知不安全默认值。

    返回问题列表；空列表表示配置安全。
    """
    problems: list[str] = []

    if not cfg.JWT_SECRET:
        problems.append("JWT_SECRET 未配置")
    elif cfg.JWT_SECRET == INSECURE_LEGACY_VALUES["JWT_SECRET"]:
        problems.append(f"JWT_SECRET 仍使用不安全的默认值 '{INSECURE_LEGACY_VALUES['JWT_SECRET']}'")

    if not cfg.ADMIN_PASSWORD:
        problems.append("ADMIN_PASSWORD 未配置")
    elif cfg.ADMIN_PASSWORD == INSECURE_LEGACY_VALUES["ADMIN_PASSWORD"]:
        problems.append(f"ADMIN_PASSWORD 仍使用不安全的默认值 'admin123'")

    return problems
