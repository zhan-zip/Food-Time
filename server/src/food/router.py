"""食物库模块 - API 路由（P0：基础搜索+详情 / P2：DIY食材接口）"""

import httpx

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from src.config import settings
from src.database import get_db
from src.food.models import Food, FoodCategory
from src.custom_food.models import CustomRecipe
from src.services.ingredient_emoji import (
    FRIDGE_CATEGORIES, SEASONING_CATEGORY,
    FRIDGE_LEFT_KEYS, FRIDGE_RIGHT_KEYS,
    INGREDIENT_EMOJI,
)

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

    # 总数（修复 H4：用 COUNT 聚合，避免把全部匹配行加载进内存再数）
    count_query = select(func.count(Food.id)).where(Food.is_public == True)
    if keyword:
        count_query = count_query.where(Food.name.like(f"%{keyword}%"))
    if cuisine:
        count_query = count_query.where(Food.cuisine == cuisine)
    if category_id:
        count_query = count_query.where(Food.category_id == category_id)

    total = (await db.execute(count_query)).scalar() or 0

    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    foods = result.scalars().all()

    # 食物 → 食谱记录映射（DIY/广场食谱），供前端判断可进详情 + 跳转广场详情页
    recipe_map_rows = await db.execute(
        select(CustomRecipe.food_id, CustomRecipe.id).where(CustomRecipe.food_id.isnot(None))
    )
    recipe_map = dict(recipe_map_rows.all())

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
                "has_recipe": f.id in recipe_map,
                "recipe_id": recipe_map.get(f.id),
                "view_count": f.view_count,
            }
            for f in foods
        ],
    }


# ============================================================
# P2-1 DIY 食材接口：按冰箱分区返回食材（含 emoji + 色条）
# 注意：必须在 /{food_id} 之前注册，否则 FastAPI 会把 /ingredients 当 food_id
# ============================================================
@router.get("/ingredients")
async def get_diy_ingredients(db: AsyncSession = Depends(get_db)):
    """获取 DIY 厨房所需的食材列表，按冰箱分区 + 调料台分组

    返回结构：
    {
      "fridge": {
        "left": [{key, label, color, items: [{id, name, emoji, food_id}]}],  # 肉类+海鲜
        "right": [{key, label, color, items: [...]}],                          # 蔬菜+豆制品+蛋奶
      },
      "seasoning": {key, label, color, items: [{id, name, emoji, food_id}]}
    }
    """
    # 收集所有食材名称
    all_names: set[str] = set()
    for cat in FRIDGE_CATEGORIES:
        all_names.update(cat["items"])
    seasoning_names = set(SEASONING_CATEGORY["items"])

    # 从数据库查询匹配的 food 记录
    all_result = await db.execute(
        select(Food).where(Food.name.in_(list(all_names)))
    )
    food_map: dict[str, Food] = {f.name: f for f in all_result.scalars().all()}

    seasoning_result = await db.execute(
        select(Food).where(Food.name.in_(list(seasoning_names)))
    )
    seasoning_food_map: dict[str, Food] = {f.name: f for f in seasoning_result.scalars().all()}

    def build_items(names: list[str], food_map_local: dict[str, Food]) -> list[dict]:
        items = []
        for name in names:
            food = food_map_local.get(name)
            items.append({
                "id": str(food.id) if food else None,
                "food_id": food.id if food else None,
                "name": name,
                "emoji": INGREDIENT_EMOJI.get(name, ""),
                "calories_per_100g": float(food.calories_per_100g) if (food and food.calories_per_100g) else None,
            })
        return items

    # 构建冰箱左门（肉类+海鲜）
    left = []
    for cat in FRIDGE_CATEGORIES:
        if cat["key"] in FRIDGE_LEFT_KEYS:
            left.append({
                "key": cat["key"],
                "label": cat["label"],
                "color": cat["color"],
                "items": build_items(cat["items"], food_map),
            })

    # 构建冰箱右门（蔬菜+豆制品+蛋奶）
    right = []
    for cat in FRIDGE_CATEGORIES:
        if cat["key"] in FRIDGE_RIGHT_KEYS:
            right.append({
                "key": cat["key"],
                "label": cat["label"],
                "color": cat["color"],
                "items": build_items(cat["items"], food_map),
            })

    # 构建调料台
    seasoning = {
        "key": SEASONING_CATEGORY["key"],
        "label": SEASONING_CATEGORY["label"],
        "color": SEASONING_CATEGORY["color"],
        "items": build_items(SEASONING_CATEGORY["items"], seasoning_food_map),
    }

    return {
        "fridge": {"left": left, "right": right},
        "seasoning": seasoning,
    }


# ============================================================
# 菜品图片代理（Pixabay）：Key 仅存服务端 .env，不暴露前端
# ============================================================
# 中文菜名 → Pixabay 英文关键词映射（Pixabay 英文搜索更准，避免中文菜名搜出不相关图）
FOOD_IMAGE_MAP = {
    "番茄炒蛋": "tomato scrambled egg",
    "西红柿炒鸡蛋": "tomato scrambled egg",
    "宫保鸡丁": "kung pao chicken",
    "黑椒牛排": "beef steak",
    "牛排": "beef steak",
    "红烧肉": "braised pork",
    "红烧排骨": "braised pork ribs",
    "麻婆豆腐": "mapo tofu",
    "水煮鱼": "spicy fish",
    "酸菜鱼": "pickled fish",
    "糖醋里脊": "sweet and sour pork",
    "鱼香肉丝": "yuxiang shredded pork",
    "回锅肉": "twice cooked pork",
    "辣子鸡": "spicy chicken",
    "可乐鸡翅": "cola chicken wings",
    "咖喱鸡": "curry chicken",
    "清蒸鱼": "steamed fish",
    "烤鱼": "grilled fish",
    "炸鸡": "fried chicken",
    "蒸蛋": "steamed egg",
    "炒蛋": "scrambled egg",
    "土豆丝": "shredded potato",
    "炒青菜": "stir fried greens",
    "青椒炒肉": "green pepper pork",
    "寿司": "sushi",
    "拉面": "ramen",
    "日式味噌汤": "miso soup",
    "味噌汤": "miso soup",
    "饺子": "dumplings",
    "包子": "steamed bun",
    "小笼包": "xiao long bao",
    "炒饭": "fried rice",
    "炒面": "chow mein",
    "火锅": "hot pot",
    "麻辣烫": "mala tang",
    "披萨": "pizza",
    "意面": "pasta",
    "三明治": "sandwich",
    "沙拉": "salad",
    "蛋糕": "cake",
    "奶茶": "milk tea",
    "冰淇淋": "ice cream",
    "蛋挞": "egg tart",
    "春卷": "spring rolls",
    "油条": "youtiao",
    "皮蛋瘦肉粥": "congee",
    "馒头": "mantou",
    "烧鹅": "roast goose",
    "烤鸭": "roast duck",
    "煎饼果子": "chinese crepe",
    "臭豆腐": "stinky tofu",
    "豆腐": "tofu",
    "毛血旺": "spicy hot pot",
    "酸辣粉": "hot and sour noodles",
    "牛肉面": "beef noodles",
    "兰州拉面": "beef noodles",
}


def _image_query(name: str) -> str:
    """中文菜名 → 英文关键词（Pixabay 英文搜索更准）；无映射则原样返回"""
    return FOOD_IMAGE_MAP.get(name, name)


_image_cache: dict[str, str] = {}


@router.get("/image")
async def food_image(query: str = Query("", description="食物名")):
    """按食物名从 Pixabay 获取菜品图片 URL（后端代理，避免 Key 泄露）"""
    query = query.strip()
    if not query:
        return {"url": None}
    # 中文菜名映射为英文关键词（Pixabay 英文搜索更准）
    search_q = _image_query(query)
    if query in _image_cache:
        return {"url": _image_cache[query] or None}
    if not settings.PIXABAY_API_KEY:
        return {"url": None}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get("https://pixabay.com/api/", params={
                "key": settings.PIXABAY_API_KEY,
                "q": search_q,
                "image_type": "photo",
                "per_page": 3,
                "safesearch": True,
            })
            hits = (r.json().get("hits") or [])
            if hits:
                url = hits[0].get("webformatURL") or hits[0].get("largeImageURL")
                _image_cache[query] = url or ""
                return {"url": url}
    except Exception as e:
        print(f"[Pixabay] 查询失败({query}): {e}")
    _image_cache[query] = ""
    return {"url": None}


@router.get("/{food_id}")
async def get_food(food_id: int, db: AsyncSession = Depends(get_db)):
    """获取食物详情（仅公开食物）"""
    # 修复 H7：仅返回公开食物，未公开/不存在统一返回 404（原实现不检查 is_public，可越权访问）
    result = await db.execute(
        select(Food).where(Food.id == food_id, Food.is_public == True)
    )
    food = result.scalar_one_or_none()
    if not food:
        raise HTTPException(status_code=404, detail="食物不存在")
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
