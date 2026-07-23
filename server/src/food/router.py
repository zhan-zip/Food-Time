"""食物库模块 - API 路由（P0：基础搜索+详情）"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from src.database import get_db
from src.food.models import Food, FoodCategory

router = APIRouter(prefix="/api/foods", tags=["食物库"])


@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """获取所有食物分类"""
    result = await db.execute(select(FoodCategory).order_by(FoodCategory.sort_order))
    categories = result.scalars().all()
    return [
        {"id": c.id, "name": c.name, "icon": c.icon, "sort_order": c.sort_order}
        for c in categories
    ]


@router.get("")
async def search_foods(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    cuisine: Optional[str] = Query(None, description="菜系"),
    category_id: Optional[int] = Query(None, description="分类ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """搜索食物（关键词+筛选+分页）"""
    query = select(Food).where(Food.is_public == True)

    if keyword:
        query = query.where(Food.name.like(f"%{keyword}%"))
    if cuisine:
        query = query.where(Food.cuisine == cuisine)
    if category_id:
        query = query.where(Food.category_id == category_id)

    # 总数
    count_query = select(Food).where(Food.is_public == True)
    if keyword:
        count_query = count_query.where(Food.name.like(f"%{keyword}%"))
    if cuisine:
        count_query = count_query.where(Food.cuisine == cuisine)
    if category_id:
        count_query = count_query.where(Food.category_id == category_id)

    total_result = await db.execute(count_query)
    total = len(total_result.scalars().all())

    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    foods = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": f.id,
                "name": f.name,
                "category_id": f.category_id,
                "image_url": f.image_url,
                "cuisine": f.cuisine,
                "tags": f.tags,
                "calories_per_100g": float(f.calories_per_100g) if f.calories_per_100g else None,
                "protein_per_100g": float(f.protein_per_100g) if f.protein_per_100g else None,
                "fat_per_100g": float(f.fat_per_100g) if f.fat_per_100g else None,
                "carbs_per_100g": float(f.carbs_per_100g) if f.carbs_per_100g else None,
                "source": f.source,
                "view_count": f.view_count,
            }
            for f in foods
        ],
    }


@router.get("/{food_id}")
async def get_food(food_id: int, db: AsyncSession = Depends(get_db)):
    """获取食物详情"""
    result = await db.execute(select(Food).where(Food.id == food_id))
    food = result.scalar_one_or_none()
    if not food:
        return {"error": "食物不存在"}
    return {
        "id": food.id,
        "name": food.name,
        "category_id": food.category_id,
        "image_url": food.image_url,
        "cuisine": food.cuisine,
        "tags": food.tags,
        "source": food.source,
        "source_url": food.source_url,
        "calories_per_100g": float(food.calories_per_100g) if food.calories_per_100g else None,
        "protein_per_100g": float(food.protein_per_100g) if food.protein_per_100g else None,
        "fat_per_100g": float(food.fat_per_100g) if food.fat_per_100g else None,
        "carbs_per_100g": float(food.carbs_per_100g) if food.carbs_per_100g else None,
        "fiber_per_100g": float(food.fiber_per_100g) if food.fiber_per_100g else None,
        "sodium_per_100g": float(food.sodium_per_100g) if food.sodium_per_100g else None,
        "view_count": food.view_count,
    }
