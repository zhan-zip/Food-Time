"""外部服务 - 邮件发送（骨架）"""

from app.config import settings


class EmailService:
    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.from_addr = settings.SMTP_FROM

    @property
    def is_configured(self) -> bool:
        return bool(self.user and self.password and self.host != "smtp.example.com")


email_service = EmailService()
