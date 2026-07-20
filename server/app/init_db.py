"""数据库初始化 - 在此导入所有模型以注册到 Base"""

from app.database import engine, Base
from app.models import *  # noqa: F401,F403


async def init_db():
    """初始化数据库表（开发用，生产请用 Alembic 迁移）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
