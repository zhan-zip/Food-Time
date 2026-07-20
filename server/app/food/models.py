"""食物库模型"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Boolean, JSON, DateTime, ForeignKey, func, Text
from app.database import Base


class FoodCategory(Base):
    __tablename__ = "food_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    icon = Column(String(100), nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())


class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("food_categories.id"), nullable=True, index=True)
    image_url = Column(String(500), nullable=True)
    cuisine = Column(String(100), nullable=True, index=True)
    tags = Column(JSON, nullable=True)
    source = Column(String(50), default="scraper")
    source_url = Column(String(500), nullable=True)
    calories_per_100g = Column(Numeric(8, 2), nullable=True)
    protein_per_100g = Column(Numeric(8, 2), nullable=True)
    fat_per_100g = Column(Numeric(8, 2), nullable=True)
    carbs_per_100g = Column(Numeric(8, 2), nullable=True)
    fiber_per_100g = Column(Numeric(8, 2), nullable=True)
    sodium_per_100g = Column(Numeric(8, 2), nullable=True)
    is_public = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
