"""认证模块 - 业务逻辑"""

import random
import string
from datetime import datetime, timedelta

import bcrypt
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.config import settings
from src.auth.models import User, EmailVerification


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode = {"sub": str(user_id), "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def generate_verification_code() -> str:
    return "".join(random.choices(string.digits, k=6))


# ---------- 用户服务 ----------

async def create_user(db: AsyncSession, email: str, password: str, nickname: str | None = None) -> User:
    user = User(
        email=email,
        password_hash=hash_password(password),
        nickname=nickname or email.split("@")[0],
        email_verified=False,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


# ---------- 邮箱验证 ----------

async def save_verification_code(db: AsyncSession, email: str) -> str:
    await db.execute(delete(EmailVerification).where(EmailVerification.email == email))
    code = generate_verification_code()
    ev = EmailVerification(
        email=email,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )
    db.add(ev)
    await db.flush()
    return code


async def verify_email_code(db: AsyncSession, email: str, code: str) -> bool:
    result = await db.execute(
        select(EmailVerification)
        .where(EmailVerification.email == email)
        .where(EmailVerification.code == code)
        .where(EmailVerification.used == False)
        .where(EmailVerification.expires_at > datetime.utcnow())
    )
    ev = result.scalar_one_or_none()
    if ev is None:
        return False
    ev.used = True
    user_result = await db.execute(select(User).where(User.email == email))
    user = user_result.scalar_one_or_none()
    if user:
        user.email_verified = True
    return True


# ---------- 管理员初始化 ----------

async def init_admin(db: AsyncSession):
    """确保管理员账号存在"""
    result = await db.execute(select(User).where(User.email == settings.ADMIN_EMAIL))
    admin = result.scalar_one_or_none()
    if admin is None:
        admin = User(
            email=settings.ADMIN_EMAIL,
            password_hash=hash_password(settings.ADMIN_PASSWORD),
            nickname="管理员",
            is_admin=True,
            email_verified=True,
        )
        db.add(admin)
        await db.flush()
        print(f"[INIT] 管理员已创建: {settings.ADMIN_EMAIL}")
    else:
        print(f"[INIT] 管理员已存在: {settings.ADMIN_EMAIL}")
