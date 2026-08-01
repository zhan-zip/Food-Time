"""管理员模块 - API 路由"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from sqlalchemy import select, func, delete

from src.database import get_db
from src.dependencies import get_admin_user
from src.auth.models import User, EmailVerification
from src.admin.models import DeletedUser
from src.custom_food.models import CustomRecipe, CustomRecipeIngredient
from src.food.models import Food
from src.diet.models import DietRecord, UserPreference
from src.expense.models import ExpenseRecord
from src.chat.models import Conversation, LongMemory
from src.public_food.models import Like, Favorite, Comment

router = APIRouter(prefix="/api/admin", tags=["管理员"])


@router.get("/stats")
async def admin_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """平台数据统计"""
    user_count = (await db.execute(select(func.count(User.id)))).scalar() or 0
    food_count = (await db.execute(select(func.count(Food.id)))).scalar() or 0
    recipe_count = (await db.execute(
        select(func.count(CustomRecipe.id)).where(CustomRecipe.publish_status == "approved")
    )).scalar() or 0
    return {
        "users": user_count,
        "foods": food_count,
        "recipes": recipe_count,
    }


# ==================== 食谱审核 ====================

@router.get("/recipes/pending")
async def list_pending_recipes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """获取待审核的食谱列表"""
    count_q = select(func.count(CustomRecipe.id)).where(
        CustomRecipe.is_published == True,
        CustomRecipe.publish_status == "pending",
    )
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    q = (
        select(CustomRecipe, Food, User)
        .join(Food, CustomRecipe.food_id == Food.id)
        .join(User, CustomRecipe.user_id == User.id)
        .where(
            CustomRecipe.is_published == True,
            CustomRecipe.publish_status == "pending",
        )
        .order_by(CustomRecipe.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    rows = (await db.execute(q)).all()

    items = []
    for recipe, food, user in rows:
        items.append({
            "id": recipe.id,
            "name": food.name,
            "author": user.nickname,
            "author_id": user.id,
            "cuisine": food.cuisine,
            "description": food.description if hasattr(food, "description") else None,
            "cooking_steps": recipe.cooking_steps,
            "calories": str(food.calories_per_100g) if food.calories_per_100g else None,
            "created_at": recipe.created_at.isoformat() if recipe.created_at else None,
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("/recipes/{recipe_id}/approve")
async def approve_recipe(
    recipe_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """审核通过食谱"""
    q = select(CustomRecipe).where(
        CustomRecipe.id == recipe_id,
        CustomRecipe.publish_status == "pending",
    )
    recipe = (await db.execute(q)).scalar_one_or_none()
    if not recipe:
        raise HTTPException(status_code=404, detail="食谱不存在或已处理")

    recipe.publish_status = "approved"
    await db.flush()
    await db.commit()
    return {"message": "审核通过", "recipe_id": recipe_id}


@router.post("/recipes/{recipe_id}/reject")
async def reject_recipe(
    recipe_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """拒绝食谱（标记为已驳回，不删除数据）"""
    q = select(CustomRecipe).where(
        CustomRecipe.id == recipe_id,
        CustomRecipe.publish_status == "pending",
    )
    recipe = (await db.execute(q)).scalar_one_or_none()
    if not recipe:
        raise HTTPException(status_code=404, detail="食谱不存在或已处理")

    recipe.publish_status = "rejected"
    await db.flush()
    await db.commit()
    return {"message": "已拒绝", "recipe_id": recipe_id}


# ==================== 用户管理 ====================

@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """获取用户列表"""
    count_q = select(func.count(User.id))
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    q = (
        select(User)
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    rows = (await db.execute(q)).scalars().all()

    items = []
    for u in rows:
        items.append({
            "id": u.id,
            "email": u.email,
            "nickname": u.nickname,
            "is_admin": u.is_admin,
            "is_active": u.is_active if hasattr(u, "is_active") else True,
            "email_verified": u.email_verified,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """更新用户（封禁/解封、设置/取消管理员）"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能操作自己的账号")

    q = select(User).where(User.id == user_id)
    user = (await db.execute(q)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if "is_admin" in body:
        user.is_admin = body["is_admin"]
    if "is_active" in body:
        user.is_active = body["is_active"]

    await db.flush()
    await db.commit()

    return {"message": "更新成功", "user_id": user_id}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """删除用户"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己的账号")

    q = select(User).where(User.id == user_id)
    user = (await db.execute(q)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 审计：删除前记录用户信息与数据摘要（后台可查看已删除用户）
    diet_count = (await db.execute(select(func.count(DietRecord.id)).where(DietRecord.user_id == user_id))).scalar() or 0
    expense_count = (await db.execute(select(func.count(ExpenseRecord.id)).where(ExpenseRecord.user_id == user_id))).scalar() or 0
    recipe_count = (await db.execute(select(func.count(CustomRecipe.id)).where(CustomRecipe.user_id == user_id))).scalar() or 0
    conversation_count = (await db.execute(select(func.count(Conversation.id)).where(Conversation.user_id == user_id))).scalar() or 0
    total_expense = (await db.execute(
        select(func.coalesce(func.sum(ExpenseRecord.amount), 0)).where(ExpenseRecord.user_id == user_id)
    )).scalar() or 0
    audit = DeletedUser(
        original_user_id=user.id,
        email=user.email,
        nickname=user.nickname,
        is_admin=user.is_admin,
        registered_at=user.created_at,
        deleted_at=datetime.now(timezone.utc),
        deleted_by=current_user.email,
        diet_count=int(diet_count),
        expense_count=int(expense_count),
        recipe_count=int(recipe_count),
        conversation_count=int(conversation_count),
        total_expense=float(total_expense or 0),
    )
    db.add(audit)
    await db.flush()

    # 修复 H10：删除用户前清理全部关联数据（防外键约束 → 500）
    recipe_ids = select(CustomRecipe.id).where(CustomRecipe.user_id == user_id)
    # 该用户菜谱的食材明细
    await db.execute(delete(CustomRecipeIngredient).where(CustomRecipeIngredient.recipe_id.in_(recipe_ids)))
    # 任何用户对该用户菜谱的点赞/收藏/评论
    await db.execute(delete(Like).where(Like.recipe_id.in_(recipe_ids)))
    await db.execute(delete(Favorite).where(Favorite.recipe_id.in_(recipe_ids)))
    await db.execute(delete(Comment).where(Comment.recipe_id.in_(recipe_ids)))
    # 该用户的菜谱
    await db.execute(delete(CustomRecipe).where(CustomRecipe.user_id == user_id))
    # 该用户的各类业务数据
    await db.execute(delete(DietRecord).where(DietRecord.user_id == user_id))
    await db.execute(delete(ExpenseRecord).where(ExpenseRecord.user_id == user_id))
    await db.execute(delete(Conversation).where(Conversation.user_id == user_id))
    await db.execute(delete(LongMemory).where(LongMemory.user_id == user_id))
    await db.execute(delete(UserPreference).where(UserPreference.user_id == user_id))
    # 该用户邮箱的验证码记录
    await db.execute(delete(EmailVerification).where(EmailVerification.email == user.email))
    # 删除用户
    await db.delete(user)
    await db.commit()

    return {"message": "用户已删除", "user_id": user_id}


# ==================== 已删除用户审计 ====================

@router.get("/deleted-users")
async def deleted_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """已删除用户审计记录（分页）"""
    total = (await db.execute(select(func.count(DeletedUser.id)))).scalar() or 0
    q = (
        select(DeletedUser)
        .order_by(DeletedUser.deleted_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = (await db.execute(q)).scalars().all()
    return {
        "items": [
            {
                "id": r.id,
                "original_user_id": r.original_user_id,
                "email": r.email,
                "nickname": r.nickname,
                "is_admin": r.is_admin,
                "registered_at": r.registered_at.isoformat() if r.registered_at else None,
                "deleted_at": r.deleted_at.isoformat() if r.deleted_at else None,
                "deleted_by": r.deleted_by,
                "diet_count": r.diet_count,
                "expense_count": r.expense_count,
                "recipe_count": r.recipe_count,
                "conversation_count": r.conversation_count,
                "total_expense": float(r.total_expense) if r.total_expense else 0,
            }
            for r in rows
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
