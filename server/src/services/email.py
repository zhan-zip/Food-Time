"""外部服务 - 邮件发送"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """邮件发送服务，支持 QQ邮箱、163邮箱等常见 SMTP"""

    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.from_addr = settings.SMTP_FROM or settings.SMTP_USER

    @property
    def is_configured(self) -> bool:
        """SMTP 是否已配置（host 不是占位值 且 有账号密码）"""
        return bool(
            self.user
            and self.password
            and self.host != "smtp.example.com"
        )

    def send(self, to_email: str, subject: str, body: str) -> bool:
        """发送纯文本邮件，返回是否成功"""
        if not self.is_configured:
            logger.warning("SMTP 未配置，跳过邮件发送")
            return False

        msg = MIMEMultipart()
        msg["From"] = self.from_addr
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        server = None
        try:
            if self.port == 465:
                # SSL 直连
                server = smtplib.SMTP_SSL(self.host, self.port, timeout=15)
            else:
                # STARTTLS
                server = smtplib.SMTP(self.host, self.port, timeout=15)
                server.starttls()

            server.login(self.user, self.password)
            server.sendmail(self.from_addr, to_email, msg.as_string())
            logger.info(f"邮件已发送: {to_email}")
            return True
        except Exception as e:
            logger.error(f"邮件发送失败 ({to_email}): {e}")
            return False
        finally:
            # 修复 M8：无论成功/失败都确保关闭 SMTP 连接，防止 socket 泄漏
            if server is not None:
                try:
                    server.quit()
                except Exception:
                    pass

    def send_verification_code(self, to_email: str, code: str) -> bool:
        """发送验证码邮件"""
        subject = "食光记 - 邮箱验证码"
        body = f"""您好！

您正在注册「食光记」，验证码如下：

    {code}

该验证码 10 分钟内有效。如非本人操作，请忽略此邮件。

---
食光记 — AI 驱动的智能饮食助手
"""
        return self.send(to_email, subject, body)


email_service = EmailService()
