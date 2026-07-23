"""对话与记忆模型"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from src.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user / assistant / system / tool
    content = Column(Text, nullable=False)
    tool_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now(), index=True)


class LongMemory(Base):
    __tablename__ = "long_memories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    fact = Column(Text, nullable=False)
    importance = Column(Integer, default=1)
    source_session = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now())
