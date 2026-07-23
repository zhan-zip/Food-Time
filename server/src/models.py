"""所有模型统一导入 - 供 Alembic 和 init_db 使用"""

from src.auth.models import User, EmailVerification
from src.food.models import FoodCategory, Food
from src.custom_food.models import CustomRecipe, CustomRecipeIngredient
from src.diet.models import DietRecord, UserPreference
from src.expense.models import ExpenseRecord
from src.chat.models import Conversation, LongMemory
from src.public_food.models import Like, Favorite, Comment

__all__ = [
    "User", "EmailVerification",
    "FoodCategory", "Food",
    "CustomRecipe", "CustomRecipeIngredient",
    "DietRecord", "UserPreference",
    "ExpenseRecord",
    "Conversation", "LongMemory",
    "Like", "Favorite", "Comment",
]
