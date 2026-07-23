"""自定义食谱模型"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Boolean, JSON, DateTime, ForeignKey, func
from src.database import Base


class CustomRecipe(Base):
    __tablename__ = "custom_recipes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    food_id = Column(Integer, ForeignKey("foods.id"), nullable=False)
    cooking_steps = Column(JSON, nullable=False)
    ai_confidence = Column(Numeric(3, 2), nullable=True)
    is_published = Column(Boolean, default=False)
    publish_status = Column(String(20), default="pending")  # pending / approved / rejected
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class CustomRecipeIngredient(Base):
    __tablename__ = "custom_recipe_ingredients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey("custom_recipes.id"), nullable=False, index=True)
    ingredient_name = Column(String(200), nullable=False)
    quantity = Column(String(100), nullable=True)
    ingredient_type = Column(String(20), nullable=False)  # ingredient / seasoning
