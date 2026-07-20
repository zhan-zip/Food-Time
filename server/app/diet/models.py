"""饮食记录与分析模型"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, JSON, Date, Time, DateTime, ForeignKey, func
from app.database import Base


class DietRecord(Base):
    __tablename__ = "diet_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    food_id = Column(Integer, ForeignKey("foods.id"), nullable=False)
    meal_type = Column(String(20), nullable=False)  # breakfast / lunch / dinner / snack
    quantity_g = Column(Numeric(8, 2), nullable=False)
    record_date = Column(Date, nullable=False, index=True)
    record_time = Column(Time, nullable=False)
    created_at = Column(DateTime, default=func.now())


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    spicy_level = Column(Numeric(3, 2), default=0)
    sweet_level = Column(Numeric(3, 2), default=0)
    hot_cold_ratio = Column(Numeric(3, 2), default=0.5)
    fav_cuisines = Column(JSON, nullable=True)
    fav_tags = Column(JSON, nullable=True)
    total_records = Column(Integer, default=0)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
