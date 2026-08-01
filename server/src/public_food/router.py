"""公共食物广场模块 - API 路由"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from src.database import get_db
from src.dependencies import get_current_user
from src.auth.models import User
from src.food.models import Food, FoodCategory
from src.custom_food.models import CustomRecipe, CustomRecipeIngredient
from src.public_food.models import Like, Favorite, Comment

router = APIRouter(prefix="/api/public", tags=["公共广场"])


# ==================== 食谱列表 ====================

@router.get("/recipes")
async def browse_recipes(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    sort_by: str = Query("time", description="time=最新 / hot=最热"),
    cuisine: str = Query("", description="筛选菜系"),
    order: str = Query("desc", description="desc=降序(最新/最热在前) / asc=升序"),
    db: AsyncSession = Depends(get_db),
):
    """浏览已发布的食谱列表（支持排序和分类筛选）"""
    # 基础条件
    conditions = [
        CustomRecipe.is_published == True,
        CustomRecipe.publish_status == "approved",
    ]
    if cuisine:
        conditions.append(Food.cuisine == cuisine)

    # 统计总数
    count_q = select(func.count(CustomRecipe.id)).join(Food, CustomRecipe.food_id == Food.id).where(and_(*conditions))
    total = (await db.execute(count_q)).scalar() or 0

    # 排序方向
    desc = order == "desc"
    order_clause = CustomRecipe.created_at.desc() if desc else CustomRecipe.created_at.asc()

    offset = (page - 1) * page_size

    if sort_by == "hot":
        # 修复 M14：热榜需按全局 hot_score 排序，不能依赖 created_at 分页
        # （旧逻辑先按时间 offset 再内存重排，第 2 页会重复/遗漏）→ 取全部候选内存排序后按页截取
        q = (
            select(CustomRecipe, Food, User)
            .join(Food, CustomRecipe.food_id == Food.id)
            .join(User, CustomRecipe.user_id == User.id)
            .where(and_(*conditions))
        )
        rows = (await db.execute(q)).all()
    else:
        q = (
            select(CustomRecipe, Food, User)
            .join(Food, CustomRecipe.food_id == Food.id)
            .join(User, CustomRecipe.user_id == User.id)
            .where(and_(*conditions))
            .order_by(order_clause)
            .offset(offset)
            .limit(page_size)
        )
        rows = (await db.execute(q)).all()

    items = []
    for recipe, food, user in rows:
        like_count = (await db.execute(
            select(func.count(Like.id)).where(Like.recipe_id == recipe.id)
        )).scalar() or 0
        fav_count = (await db.execute(
            select(func.count(Favorite.id)).where(Favorite.recipe_id == recipe.id)
        )).scalar() or 0

        items.append({
            "id": recipe.id,
            "name": food.name,
            "cuisine": food.cuisine,
            "tags": food.tags,
            "image_url": food.image_url,
            "author": user.nickname,
            "calories": str(food.calories_per_100g) if food.calories_per_100g else None,
            "like_count": like_count,
            "fav_count": fav_count,
            "hot_score": like_count * 2 + fav_count,
            "created_at": recipe.created_at.isoformat() if recipe.created_at else None,
        })

    # 热度排序（全局 hot_score 排序后按页截取）
    if sort_by == "hot":
        items.sort(key=lambda x: x["hot_score"], reverse=desc)
        items = items[offset:offset + page_size]

    return {"items": items, "total": total, "page": page, "page_size": page_size, "sort_by": sort_by, "cuisine": cuisine, "order": order}


# ==================== 食谱详情 ====================

@router.get("/recipes/{recipe_id}")
async def get_recipe_detail(
    recipe_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取食谱详情（含食材、步骤、评论数）"""
    q = (
        select(CustomRecipe, Food, User, FoodCategory)
        .join(Food, CustomRecipe.food_id == Food.id)
        .join(User, CustomRecipe.user_id == User.id)
        .outerjoin(FoodCategory, Food.category_id == FoodCategory.id)
        .where(
            CustomRecipe.id == recipe_id,
            CustomRecipe.is_published == True,
            CustomRecipe.publish_status == "approved",
        )
    )
    row = (await db.execute(q)).first()
    if not row:
        raise HTTPException(status_code=404, detail="食谱不存在")

    recipe, food, user, category = row

    # 食材列表
    ing_q = (
        select(CustomRecipeIngredient)
        .where(CustomRecipeIngredient.recipe_id == recipe_id)
        .order_by(CustomRecipeIngredient.id)
    )
    ingredients = (await db.execute(ing_q)).scalars().all()

    materials = []
    seasonings = []
    for ing in ingredients:
        item = {"name": ing.ingredient_name, "quantity": ing.quantity}
        if ing.ingredient_type == "ingredient":
            materials.append(item)
        else:
            seasonings.append(item)

    # 统计
    like_count = (await db.execute(
        select(func.count(Like.id)).where(Like.recipe_id == recipe_id)
    )).scalar() or 0
    fav_count = (await db.execute(
        select(func.count(Favorite.id)).where(Favorite.recipe_id == recipe_id)
    )).scalar() or 0
    comment_count = (await db.execute(
        select(func.count(Comment.id)).where(Comment.recipe_id == recipe_id)
    )).scalar() or 0

    return {
        "id": recipe.id,
        "food_id": food.id,
        "name": food.name,
        "author": user.nickname,
        "author_id": user.id,
        "cuisine": food.cuisine,
        "category": category.name if category else None,
        "tags": food.tags,
        "image_url": food.image_url,
        "description": food.description if hasattr(food, "description") else None,
        "calories": str(food.calories_per_100g) if food.calories_per_100g else None,
        "protein": str(food.protein_per_100g) if food.protein_per_100g else None,
        "fat": str(food.fat_per_100g) if food.fat_per_100g else None,
        "carbs": str(food.carbs_per_100g) if food.carbs_per_100g else None,
        "materials": materials,
        "seasonings": seasonings,
        "steps": recipe.cooking_steps,
        "ai_confidence": str(recipe.ai_confidence) if recipe.ai_confidence else None,
        "like_count": like_count,
        "fav_count": fav_count,
        "comment_count": comment_count,
        "source": food.source if hasattr(food, "source") else None,
        "created_at": recipe.created_at.isoformat() if recipe.created_at else None,
    }


# ==================== 评论 ====================

@router.get("/recipes/{recipe_id}/comments")
async def get_comments(
    recipe_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取食谱评论列表"""
    q = (
        select(Comment, User)
        .join(User, Comment.user_id == User.id)
        .where(Comment.recipe_id == recipe_id)
        .order_by(Comment.created_at.desc())
    )
    rows = (await db.execute(q)).all()

    return {
        "comments": [
            {
                "id": c.id,
                "user": u.nickname,
                "content": c.content,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c, u in rows
        ]
    }


@router.post("/recipes/{recipe_id}/comment")
async def add_comment(
    recipe_id: int,
    content: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """添加评论"""
    text = content.get("content", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="评论内容不能为空")

    comment = Comment(recipe_id=recipe_id, user_id=current_user.id, content=text)
    db.add(comment)
    await db.flush()
    await db.refresh(comment)

    return {
        "id": comment.id,
        "user": current_user.nickname,
        "content": comment.content,
        "created_at": comment.created_at.isoformat() if comment.created_at else None,
    }


# ==================== 收藏到个人食物库 ====================

@router.post("/recipes/{recipe_id}/save")
async def save_to_my_foods(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """将食谱收藏到个人食物库"""
    # 检查食谱是否存在
    recipe_q = select(CustomRecipe).where(CustomRecipe.id == recipe_id)
    recipe = (await db.execute(recipe_q)).scalar_one_or_none()
    if not recipe:
        raise HTTPException(status_code=404, detail="食谱不存在")

    # 检查是否已收藏
    exist_q = select(Favorite).where(
        and_(Favorite.user_id == current_user.id, Favorite.recipe_id == recipe_id)
    )
    existing = (await db.execute(exist_q)).scalar_one_or_none()
    if existing:
        return {"message": "已收藏", "saved": False}

    fav = Favorite(user_id=current_user.id, recipe_id=recipe_id)
    db.add(fav)
    await db.flush()

    return {"message": "已添加到我的食物库", "saved": True}


@router.delete("/recipes/{recipe_id}/save")
async def remove_from_my_foods(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """从个人食物库移除"""
    exist_q = select(Favorite).where(
        and_(Favorite.user_id == current_user.id, Favorite.recipe_id == recipe_id)
    )
    existing = (await db.execute(exist_q)).scalar_one_or_none()
    if existing:
        await db.delete(existing)
        await db.flush()
        return {"message": "已移除收藏"}
    return {"message": "未收藏过"}
