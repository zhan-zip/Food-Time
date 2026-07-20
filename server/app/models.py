"""所有模型统一导入 - 供 Alembic 和 init_db 使用"""

from app.auth.models import User, EmailVerification
from app.food.models import FoodCategory, Food
from app.custom_food.models import CustomRecipe, CustomRecipeIngredient
from app.diet.models import DietRecord, UserPreference
from app.expense.models import ExpenseRecord
from app.chat.models import Conversation, LongMemory
from app.public_food.models import Like, Favorite

__all__ = [
    "User", "EmailVerification",
    "FoodCategory", "Food",
    "CustomRecipe", "CustomRecipeIngredient",
    "DietRecord", "UserPreference",
    "ExpenseRecord",
    "Conversation", "LongMemory",
    "Like", "Favorite",
]
