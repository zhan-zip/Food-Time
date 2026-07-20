"""公共广场模型"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, func, UniqueConstraint
from app.database import Base


class Like(Base):
    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint("user_id", "recipe_id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("custom_recipes.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "recipe_id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("custom_recipes.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
