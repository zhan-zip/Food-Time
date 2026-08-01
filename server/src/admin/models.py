"""管理员模块 - 删除用户审计记录模型"""

from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime, func
from src.database import Base


class DeletedUser(Base):
    """被删除用户的审计记录（删除时存档，后台可查看已删除用户数据）"""

    __tablename__ = "deleted_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_user_id = Column(Integer, nullable=False, index=True)  # 原用户ID
    email = Column(String(255), nullable=False)
    nickname = Column(String(100), nullable=False)
    is_admin = Column(Boolean, default=False)
    registered_at = Column(DateTime, nullable=True)      # 原注册时间
    deleted_at = Column(DateTime, default=func.now())    # 删除时间
    deleted_by = Column(String(255), nullable=True)      # 操作管理员邮箱
    # 数据摘要
    diet_count = Column(Integer, default=0)              # 饮食记录数
    expense_count = Column(Integer, default=0)           # 账单数
    recipe_count = Column(Integer, default=0)            # 菜谱数
    conversation_count = Column(Integer, default=0)      # 对话数
    total_expense = Column(Numeric(12, 2), default=0)    # 累计消费金额
