"""账单记录模型"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, func
from app.database import Base


class ExpenseRecord(Base):
    __tablename__ = "expense_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    category = Column(String(50), nullable=False)  # food / shopping / transport / entertainment / other
    description = Column(String(500), nullable=True)
    record_date = Column(Date, nullable=False, index=True)
    input_method = Column(String(20), default="manual")  # manual / ocr
    ocr_image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now())
