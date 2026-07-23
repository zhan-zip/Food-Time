"""种子数据 - 初始化食物分类和基础食物"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.food.models import FoodCategory, Food
from src.database import async_session


CATEGORIES = [
    {"name": "川菜", "icon": "fire-o", "sort_order": 1},
    {"name": "粤菜", "icon": "smile-o", "sort_order": 2},
    {"name": "湘菜", "icon": "warning-o", "sort_order": 3},
    {"name": "鲁菜", "icon": "flower-o", "sort_order": 4},
    {"name": "日料", "icon": "star-o", "sort_order": 5},
    {"name": "韩餐", "icon": "fire-o", "sort_order": 6},
    {"name": "西餐", "icon": "gift-o", "sort_order": 7},
    {"name": "小吃", "icon": "shop-o", "sort_order": 8},
    {"name": "甜品", "icon": "like-o", "sort_order": 9},
    {"name": "饮品", "icon": "drink", "sort_order": 10},
    {"name": "面食", "icon": "label-o", "sort_order": 11},
    {"name": "粥汤", "icon": "hot-o", "sort_order": 12},
]

SAMPLE_FOODS = [
    # (名称, 分类名, 菜系, 标签JSON, 热量, 蛋白质, 脂肪, 碳水)
    ("麻婆豆腐", "川菜", "川菜", '{"spicy":"high","temp":"hot","cooking":"stir-fry"}', 120, 8.0, 7.0, 6.0),
    ("宫保鸡丁", "川菜", "川菜", '{"spicy":"medium","temp":"hot","cooking":"stir-fry"}', 170, 16.0, 10.0, 5.0),
    ("水煮鱼", "川菜", "川菜", '{"spicy":"high","temp":"hot","cooking":"boil"}', 135, 18.0, 5.5, 2.0),
    ("白切鸡", "粤菜", "粤菜", '{"spicy":"none","temp":"warm","cooking":"boil"}', 160, 19.0, 9.0, 0.5),
    ("叉烧", "粤菜", "粤菜", '{"spicy":"none","temp":"warm","cooking":"roast"}', 260, 22.0, 16.0, 8.0),
    ("虾饺", "粤菜", "粤菜", '{"spicy":"none","temp":"hot","cooking":"steam"}', 200, 8.0, 5.0, 30.0),
    ("剁椒鱼头", "湘菜", "湘菜", '{"spicy":"high","temp":"hot","cooking":"steam"}', 110, 15.0, 4.0, 3.0),
    ("红烧肉", "鲁菜", "鲁菜", '{"spicy":"none","temp":"hot","cooking":"braise"}', 320, 12.0, 28.0, 5.0),
    ("寿司", "日料", "日料", '{"spicy":"none","temp":"cold","cooking":"raw"}', 150, 4.0, 1.0, 28.0),
    ("拉面", "日料", "日料", '{"spicy":"none","temp":"hot","cooking":"boil"}', 110, 4.0, 1.5, 20.0),
    ("石锅拌饭", "韩餐", "韩餐", '{"spicy":"medium","temp":"hot","cooking":"mix"}', 180, 6.0, 5.0, 28.0),
    ("韩式炸鸡", "韩餐", "韩餐", '{"spicy":"medium","temp":"hot","cooking":"fry"}', 280, 20.0, 18.0, 12.0),
    ("牛排", "西餐", "西餐", '{"spicy":"none","temp":"hot","cooking":"grill"}', 250, 26.0, 15.0, 1.0),
    ("意面", "西餐", "西餐", '{"spicy":"none","temp":"hot","cooking":"boil"}', 160, 5.0, 2.0, 30.0),
    ("煎饼果子", "小吃", "小吃", '{"spicy":"low","temp":"hot","cooking":"fry"}', 210, 6.0, 8.0, 28.0),
    ("臭豆腐", "小吃", "小吃", '{"spicy":"medium","temp":"hot","cooking":"fry"}', 130, 8.0, 7.0, 8.0),
    ("提拉米苏", "甜品", "甜品", '{"spicy":"none","temp":"cold","cooking":"bake"}', 350, 6.0, 20.0, 35.0),
    ("奶茶", "饮品", "饮品", '{"spicy":"none","temp":"cold","cooking":"mix"}', 80, 1.0, 2.0, 14.0),
    ("兰州拉面", "面食", "面食", '{"spicy":"low","temp":"hot","cooking":"boil"}', 120, 5.0, 2.0, 22.0),
    ("皮蛋瘦肉粥", "粥汤", "粥汤", '{"spicy":"none","temp":"hot","cooking":"boil"}', 60, 4.0, 2.0, 8.0),
]


async def seed_all(db: AsyncSession):
    """初始化种子数据（幂等，重复执行不会重复插入）"""
    await seed_categories(db)
    await seed_foods(db)


async def seed_categories(db: AsyncSession):
    result = await db.execute(select(FoodCategory).limit(1))
    if result.scalar_one_or_none():
        print("[SEED] 食物分类已存在，跳过")
        return

    for cat in CATEGORIES:
        db.add(FoodCategory(**cat))
    await db.flush()
    print(f"[SEED] 已插入 {len(CATEGORIES)} 个食物分类")


async def seed_foods(db: AsyncSession):
    result = await db.execute(select(Food).limit(1))
    if result.scalar_one_or_none():
        print("[SEED] 食物数据已存在，跳过")
        return

    # 先获取分类映射
    cat_result = await db.execute(select(FoodCategory))
    cat_map = {c.name: c.id for c in cat_result.scalars().all()}

    for name, cat_name, cuisine, tags, cal, pro, fat, carbs in SAMPLE_FOODS:
        db.add(Food(
            name=name,
            category_id=cat_map.get(cat_name),
            cuisine=cuisine,
            tags=tags,
            source="seed",
            calories_per_100g=cal,
            protein_per_100g=pro,
            fat_per_100g=fat,
            carbs_per_100g=carbs,
            is_public=True,
        ))
    await db.flush()
    print(f"[SEED] 已插入 {len(SAMPLE_FOODS)} 条食物数据")


if __name__ == "__main__":
    asyncio.run(seed_all(async_session()))
