"""种子数据 - 初始化食物分类和基础食物"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.food.models import FoodCategory, Food
from src.auth.models import User
from src.custom_food.models import CustomRecipe, CustomRecipeIngredient
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
    ("麻婆豆腐", "川菜", "川菜", {"spicy":"high","temp":"hot","cooking":"stir-fry"}, 120, 8.0, 7.0, 6.0),
    ("宫保鸡丁", "川菜", "川菜", {"spicy":"medium","temp":"hot","cooking":"stir-fry"}, 170, 16.0, 10.0, 5.0),
    ("水煮鱼", "川菜", "川菜", {"spicy":"high","temp":"hot","cooking":"boil"}, 135, 18.0, 5.5, 2.0),
    ("白切鸡", "粤菜", "粤菜", {"spicy":"none","temp":"warm","cooking":"boil"}, 160, 19.0, 9.0, 0.5),
    ("叉烧", "粤菜", "粤菜", {"spicy":"none","temp":"warm","cooking":"roast"}, 260, 22.0, 16.0, 8.0),
    ("虾饺", "粤菜", "粤菜", {"spicy":"none","temp":"hot","cooking":"steam"}, 200, 8.0, 5.0, 30.0),
    ("剁椒鱼头", "湘菜", "湘菜", {"spicy":"high","temp":"hot","cooking":"steam"}, 110, 15.0, 4.0, 3.0),
    ("红烧肉", "鲁菜", "鲁菜", {"spicy":"none","temp":"hot","cooking":"braise"}, 320, 12.0, 28.0, 5.0),
    ("寿司", "日料", "日料", {"spicy":"none","temp":"cold","cooking":"raw"}, 150, 4.0, 1.0, 28.0),
    ("拉面", "日料", "日料", {"spicy":"none","temp":"hot","cooking":"boil"}, 110, 4.0, 1.5, 20.0),
    ("石锅拌饭", "韩餐", "韩餐", {"spicy":"medium","temp":"hot","cooking":"mix"}, 180, 6.0, 5.0, 28.0),
    ("韩式炸鸡", "韩餐", "韩餐", {"spicy":"medium","temp":"hot","cooking":"fry"}, 280, 20.0, 18.0, 12.0),
    ("牛排", "西餐", "西餐", {"spicy":"none","temp":"hot","cooking":"grill"}, 250, 26.0, 15.0, 1.0),
    ("意面", "西餐", "西餐", {"spicy":"none","temp":"hot","cooking":"boil"}, 160, 5.0, 2.0, 30.0),
    ("煎饼果子", "小吃", "小吃", {"spicy":"low","temp":"hot","cooking":"fry"}, 210, 6.0, 8.0, 28.0),
    ("臭豆腐", "小吃", "小吃", {"spicy":"medium","temp":"hot","cooking":"fry"}, 130, 8.0, 7.0, 8.0),
    ("提拉米苏", "甜品", "甜品", {"spicy":"none","temp":"cold","cooking":"bake"}, 350, 6.0, 20.0, 35.0),
    ("奶茶", "饮品", "饮品", {"spicy":"none","temp":"cold","cooking":"mix"}, 80, 1.0, 2.0, 14.0),
    ("兰州拉面", "面食", "面食", {"spicy":"low","temp":"hot","cooking":"boil"}, 120, 5.0, 2.0, 22.0),
    ("皮蛋瘦肉粥", "粥汤", "粥汤", {"spicy":"none","temp":"hot","cooking":"boil"}, 60, 4.0, 2.0, 8.0),
    # === 扩充数据 - 川菜 ===
    ("回锅肉", "川菜", "川菜", {"spicy":"medium","temp":"hot","cooking":"stir-fry"}, 240, 14.0, 18.0, 6.0),
    ("鱼香肉丝", "川菜", "川菜", {"spicy":"medium","temp":"hot","cooking":"stir-fry"}, 155, 12.0, 9.0, 8.0),
    ("担担面", "川菜", "川菜", {"spicy":"medium","temp":"hot","cooking":"boil"}, 130, 6.0, 5.0, 18.0),
    ("酸菜鱼", "川菜", "川菜", {"spicy":"medium","temp":"hot","cooking":"boil"}, 100, 15.0, 3.5, 2.0),
    ("毛血旺", "川菜", "川菜", {"spicy":"high","temp":"hot","cooking":"boil"}, 180, 14.0, 12.0, 4.0),
    # === 扩充数据 - 粤菜 ===
    ("烧鹅", "粤菜", "粤菜", {"spicy":"none","temp":"warm","cooking":"roast"}, 280, 20.0, 22.0, 2.0),
    ("肠粉", "粤菜", "粤菜", {"spicy":"none","temp":"hot","cooking":"steam"}, 110, 3.0, 2.0, 20.0),
    ("煲仔饭", "粤菜", "粤菜", {"spicy":"none","temp":"hot","cooking":"braise"}, 180, 8.0, 6.0, 25.0),
    ("云吞面", "粤菜", "粤菜", {"spicy":"none","temp":"hot","cooking":"boil"}, 100, 5.0, 2.0, 16.0),
    ("干炒牛河", "粤菜", "粤菜", {"spicy":"low","temp":"hot","cooking":"stir-fry"}, 190, 8.0, 7.0, 25.0),
    # === 扩充数据 - 湘菜 ===
    ("辣椒炒肉", "湘菜", "湘菜", {"spicy":"high","temp":"hot","cooking":"stir-fry"}, 185, 15.0, 12.0, 5.0),
    ("外婆菜", "湘菜", "湘菜", {"spicy":"medium","temp":"hot","cooking":"stir-fry"}, 90, 5.0, 4.0, 10.0),
    ("小炒黄牛肉", "湘菜", "湘菜", {"spicy":"high","temp":"hot","cooking":"stir-fry"}, 160, 18.0, 8.0, 4.0),
    ("口味虾", "湘菜", "湘菜", {"spicy":"high","temp":"hot","cooking":"stir-fry"}, 130, 16.0, 5.0, 4.0),
    # === 扩充数据 - 鲁菜 ===
    ("糖醋里脊", "鲁菜", "鲁菜", {"spicy":"none","temp":"hot","cooking":"fry"}, 210, 14.0, 10.0, 18.0),
    ("葱烧海参", "鲁菜", "鲁菜", {"spicy":"none","temp":"hot","cooking":"braise"}, 80, 8.0, 2.0, 6.0),
    ("九转大肠", "鲁菜", "鲁菜", {"spicy":"low","temp":"hot","cooking":"braise"}, 260, 12.0, 20.0, 8.0),
    ("锅塌豆腐", "鲁菜", "鲁菜", {"spicy":"none","temp":"hot","cooking":"fry"}, 140, 10.0, 8.0, 8.0),
    # === 扩充数据 - 日料 ===
    ("天妇罗", "日料", "日料", {"spicy":"none","temp":"hot","cooking":"fry"}, 230, 5.0, 14.0, 20.0),
    ("味噌拉面", "日料", "日料", {"spicy":"none","temp":"hot","cooking":"boil"}, 120, 6.0, 3.5, 18.0),
    ("日式咖喱饭", "日料", "日料", {"spicy":"low","temp":"hot","cooking":"braise"}, 160, 7.0, 5.0, 22.0),
    ("大阪烧", "日料", "日料", {"spicy":"none","temp":"hot","cooking":"fry"}, 200, 8.0, 10.0, 20.0),
    ("鳗鱼饭", "日料", "日料", {"spicy":"none","temp":"hot","cooking":"grill"}, 220, 14.0, 10.0, 22.0),
    # === 扩充数据 - 韩餐 ===
    ("韩式烤肉", "韩餐", "韩餐", {"spicy":"low","temp":"hot","cooking":"grill"}, 270, 22.0, 20.0, 2.0),
    ("泡菜汤", "韩餐", "韩餐", {"spicy":"medium","temp":"hot","cooking":"boil"}, 60, 5.0, 3.0, 5.0),
    ("韩式冷面", "韩餐", "韩餐", {"spicy":"medium","temp":"cold","cooking":"boil"}, 100, 4.0, 1.0, 20.0),
    ("韩式炒年糕", "韩餐", "韩餐", {"spicy":"medium","temp":"hot","cooking":"stir-fry"}, 180, 3.0, 3.0, 35.0),
    # === 扩充数据 - 西餐 ===
    ("披萨", "西餐", "西餐", {"spicy":"none","temp":"hot","cooking":"bake"}, 270, 12.0, 10.0, 33.0),
    ("凯撒沙拉", "西餐", "西餐", {"spicy":"none","temp":"cold","cooking":"raw"}, 120, 8.0, 7.0, 6.0),
    ("汉堡", "西餐", "西餐", {"spicy":"none","temp":"hot","cooking":"grill"}, 290, 16.0, 14.0, 28.0),
    ("奶油蘑菇汤", "西餐", "西餐", {"spicy":"none","temp":"hot","cooking":"boil"}, 90, 3.0, 6.0, 7.0),
    ("法式焗蜗牛", "西餐", "西餐", {"spicy":"none","temp":"hot","cooking":"bake"}, 120, 10.0, 7.0, 3.0),
    # === 扩充数据 - 小吃 ===
    ("肉夹馍", "小吃", "小吃", {"spicy":"low","temp":"hot","cooking":"braise"}, 230, 12.0, 10.0, 24.0),
    ("麻辣烫", "小吃", "小吃", {"spicy":"medium","temp":"hot","cooking":"boil"}, 80, 6.0, 4.0, 6.0),
    ("烤串", "小吃", "小吃", {"spicy":"medium","temp":"hot","cooking":"grill"}, 220, 18.0, 15.0, 3.0),
    ("凉皮", "小吃", "小吃", {"spicy":"low","temp":"cold","cooking":"mix"}, 110, 4.0, 3.0, 18.0),
    ("生煎包", "小吃", "小吃", {"spicy":"none","temp":"hot","cooking":"fry"}, 200, 8.0, 9.0, 22.0),
    ("鸡蛋灌饼", "小吃", "小吃", {"spicy":"low","temp":"hot","cooking":"fry"}, 220, 8.0, 10.0, 26.0),
    ("酸辣粉", "小吃", "小吃", {"spicy":"high","temp":"hot","cooking":"boil"}, 100, 3.0, 2.0, 18.0),
    # === 扩充数据 - 甜品 ===
    ("芒果班戟", "甜品", "甜品", {"spicy":"none","temp":"cold","cooking":"mix"}, 220, 4.0, 12.0, 25.0),
    ("双皮奶", "甜品", "甜品", {"spicy":"none","temp":"cold","cooking":"steam"}, 120, 5.0, 5.0, 14.0),
    ("杨枝甘露", "甜品", "甜品", {"spicy":"none","temp":"cold","cooking":"mix"}, 100, 2.0, 3.0, 18.0),
    ("蛋挞", "甜品", "甜品", {"spicy":"none","temp":"warm","cooking":"bake"}, 300, 5.0, 18.0, 30.0),
    ("红豆沙", "甜品", "甜品", {"spicy":"none","temp":"hot","cooking":"boil"}, 150, 6.0, 1.0, 30.0),
    # === 扩充数据 - 饮品 ===
    ("豆浆", "饮品", "饮品", {"spicy":"none","temp":"hot","cooking":"mix"}, 30, 3.0, 1.5, 1.5),
    ("酸梅汤", "饮品", "饮品", {"spicy":"none","temp":"cold","cooking":"boil"}, 40, 0.5, 0.2, 10.0),
    ("珍珠奶茶", "饮品", "饮品", {"spicy":"none","temp":"cold","cooking":"mix"}, 90, 2.0, 3.0, 16.0),
    ("美式咖啡", "饮品", "饮品", {"spicy":"none","temp":"hot","cooking":"brew"}, 5, 0.3, 0, 1.0),
    ("椰汁", "饮品", "饮品", {"spicy":"none","temp":"cold","cooking":"mix"}, 50, 0.5, 3.0, 6.0),
    # === 扩充数据 - 面食 ===
    ("炸酱面", "面食", "面食", {"spicy":"low","temp":"hot","cooking":"boil"}, 160, 8.0, 6.0, 22.0),
    ("油泼面", "面食", "面食", {"spicy":"medium","temp":"hot","cooking":"boil"}, 170, 6.0, 7.0, 24.0),
    ("刀削面", "面食", "面食", {"spicy":"low","temp":"hot","cooking":"boil"}, 130, 5.0, 2.5, 22.0),
    ("热干面", "面食", "面食", {"spicy":"low","temp":"hot","cooking":"boil"}, 170, 6.0, 7.0, 22.0),
    ("阳春面", "面食", "面食", {"spicy":"none","temp":"hot","cooking":"boil"}, 100, 4.0, 1.5, 20.0),
    # === 扩充数据 - 粥汤 ===
    ("南瓜粥", "粥汤", "粥汤", {"spicy":"none","temp":"hot","cooking":"boil"}, 40, 1.0, 0.5, 9.0),
    ("排骨汤", "粥汤", "粥汤", {"spicy":"none","temp":"hot","cooking":"boil"}, 70, 8.0, 4.0, 2.0),
    ("银耳莲子羹", "粥汤", "粥汤", {"spicy":"none","temp":"hot","cooking":"boil"}, 55, 1.5, 0.5, 12.0),
    ("冬瓜排骨汤", "粥汤", "粥汤", {"spicy":"none","temp":"hot","cooking":"boil"}, 50, 5.0, 2.5, 2.0),
    ("酸辣汤", "粥汤", "粥汤", {"spicy":"medium","temp":"hot","cooking":"boil"}, 45, 3.0, 1.5, 5.0),
    # === 扩充数据 - 混合菜系 ===
    ("火锅（川味）", "川菜", "川菜", {"spicy":"high","temp":"hot","cooking":"boil"}, 200, 15.0, 14.0, 8.0),
    ("清蒸鲈鱼", "粤菜", "粤菜", {"spicy":"none","temp":"hot","cooking":"steam"}, 105, 18.0, 3.5, 1.0),
    ("糖醋排骨", "鲁菜", "鲁菜", {"spicy":"none","temp":"hot","cooking":"braise"}, 280, 16.0, 18.0, 15.0),
    ("黄焖鸡米饭", "鲁菜", "鲁菜", {"spicy":"low","temp":"hot","cooking":"braise"}, 150, 14.0, 7.0, 10.0),
    ("新疆大盘鸡", "面食", "面食", {"spicy":"medium","temp":"hot","cooking":"braise"}, 170, 14.0, 8.0, 12.0),
    ("螺蛳粉", "小吃", "小吃", {"spicy":"medium","temp":"hot","cooking":"boil"}, 130, 4.0, 5.0, 18.0),
    ("冰粉", "甜品", "甜品", {"spicy":"none","temp":"cold","cooking":"mix"}, 45, 0.5, 0.2, 11.0),
    ("豆腐脑", "小吃", "小吃", {"spicy":"low","temp":"hot","cooking":"steam"}, 50, 4.0, 2.0, 4.0),
    ("锅包肉", "鲁菜", "鲁菜", {"spicy":"none","temp":"hot","cooking":"fry"}, 260, 14.0, 16.0, 18.0),
    ("钵钵鸡", "川菜", "川菜", {"spicy":"high","temp":"cold","cooking":"boil"}, 140, 18.0, 6.0, 2.0),
    ("煲汤（老火汤）", "粤菜", "粤菜", {"spicy":"none","temp":"hot","cooking":"boil"}, 40, 3.0, 1.0, 4.0),
    ("三文鱼刺身", "日料", "日料", {"spicy":"none","temp":"cold","cooking":"raw"}, 180, 20.0, 10.0, 1.0),
    ("参鸡汤", "韩餐", "韩餐", {"spicy":"none","temp":"hot","cooking":"boil"}, 80, 12.0, 3.0, 3.0),
    ("蔬菜沙拉", "西餐", "西餐", {"spicy":"none","temp":"cold","cooking":"raw"}, 40, 2.0, 2.5, 3.0),
    ("柠檬水", "饮品", "饮品", {"spicy":"none","temp":"cold","cooking":"mix"}, 20, 0.2, 0.1, 5.0),
    ("八宝粥", "粥汤", "粥汤", {"spicy":"none","temp":"hot","cooking":"boil"}, 80, 3.0, 1.0, 17.0),
    ("龙抄手", "川菜", "川菜", {"spicy":"medium","temp":"hot","cooking":"boil"}, 140, 10.0, 7.0, 12.0),
    ("馕", "面食", "面食", {"spicy":"none","temp":"warm","cooking":"bake"}, 260, 8.0, 2.0, 52.0),
    ("疙瘩汤", "粥汤", "粥汤", {"spicy":"none","temp":"hot","cooking":"boil"}, 50, 2.0, 1.0, 9.0),
    ("盐酥鸡", "小吃", "小吃", {"spicy":"low","temp":"hot","cooking":"fry"}, 250, 16.0, 15.0, 12.0),
    ("龟苓膏", "甜品", "甜品", {"spicy":"none","temp":"cold","cooking":"boil"}, 60, 1.0, 0.5, 14.0),
    ("珍珠丸子", "粤菜", "粤菜", {"spicy":"none","temp":"hot","cooking":"steam"}, 170, 10.0, 8.0, 16.0),
    ("芋圆", "甜品", "甜品", {"spicy":"none","temp":"cold","cooking":"boil"}, 120, 2.0, 1.5, 26.0),
    ("乌冬面", "日料", "日料", {"spicy":"none","temp":"hot","cooking":"boil"}, 100, 3.5, 1.0, 20.0),
    ("凉面", "面食", "面食", {"spicy":"low","temp":"cold","cooking":"boil"}, 140, 5.0, 4.0, 22.0),
    ("绿豆汤", "饮品", "饮品", {"spicy":"none","temp":"cold","cooking":"boil"}, 35, 1.5, 0.2, 7.0),
    ("酱骨头", "鲁菜", "鲁菜", {"spicy":"none","temp":"hot","cooking":"braise"}, 220, 20.0, 15.0, 2.0),
    ("炸酱面", "面食", "面食", {"spicy":"low","temp":"hot","cooking":"boil"}, 160, 8.0, 6.0, 22.0),
]


async def seed_all(db: AsyncSession):
    """初始化种子数据（幂等，重复执行不会重复插入）"""
    await seed_categories(db)
    await seed_foods(db)
    await seed_recipes(db)


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


SAMPLE_RECIPES = [
    {
        "name": "番茄炒蛋",
        "description": "一道经典的家常菜，酸甜可口，做法简单，是每个中国家庭的必备菜式。番茄的酸甜与鸡蛋的嫩滑完美结合，配米饭绝佳。",
        "cuisine": "川菜",
        "category": "川菜",
        "tags": {"spicy":"none","temp":"hot","cooking":"stir-fry","level":"entry"},
        "calories": 85, "protein": 5.0, "fat": 6.0, "carbs": 4.0,
        "materials": [{"name": "番茄", "quantity": "2个"}, {"name": "鸡蛋", "quantity": "3个"}],
        "seasonings": [{"name": "盐", "quantity": "适量"}, {"name": "糖", "quantity": "1茶匙"}, {"name": "葱花", "quantity": "少许"}],
        "steps": [
            "番茄洗净切块，鸡蛋打散加少许盐搅匀",
            "热锅倒油，倒入蛋液炒至凝固盛出",
            "锅中留底油，倒入番茄块翻炒出汁",
            "加糖调味，倒回鸡蛋翻炒均匀",
            "撒上葱花即可出锅"
        ],
    },
    {
        "name": "宫保鸡丁（家常版）",
        "description": "宫保鸡丁是川菜中最具国际知名度的菜品之一，鸡丁嫩滑、花生酥脆、麻辣香甜。这个家常版简化了部分步骤，适合家庭厨房。",
        "cuisine": "川菜",
        "category": "川菜",
        "tags": {"spicy":"medium","temp":"hot","cooking":"stir-fry","level":"medium"},
        "calories": 160, "protein": 14.0, "fat": 9.0, "carbs": 8.0,
        "materials": [{"name": "鸡胸肉", "quantity": "300g"}, {"name": "花生米", "quantity": "50g"}, {"name": "黄瓜", "quantity": "半根"}, {"name": "胡萝卜", "quantity": "半根"}],
        "seasonings": [{"name": "干辣椒", "quantity": "5-6个"}, {"name": "花椒", "quantity": "1茶匙"}, {"name": "酱油", "quantity": "2汤匙"}, {"name": "醋", "quantity": "1汤匙"}, {"name": "糖", "quantity": "1汤匙"}, {"name": "淀粉", "quantity": "适量"}, {"name": "姜蒜", "quantity": "适量"}],
        "steps": [
            "鸡胸肉切丁，加料酒、淀粉、少许盐腌制15分钟",
            "黄瓜、胡萝卜切丁备用",
            "调酱汁：酱油、醋、糖、淀粉加水调匀",
            "热锅凉油，小火炸花生米至金黄捞出",
            "锅中留底油，爆香花椒干辣椒和姜蒜",
            "下鸡丁翻炒变色，加入胡萝卜丁翻炒",
            "倒入酱汁翻炒均匀，加入黄瓜丁和花生米",
            "大火收汁即可"
        ],
    },
    {
        "name": "日式味噌汤",
        "description": "日本料理中最基础的汤品，味道鲜美醇厚，富含蛋白质和益生菌。只需几种简单食材，就能做出一碗暖心暖胃的美味汤品。",
        "cuisine": "日料",
        "category": "日料",
        "tags": {"spicy":"none","temp":"hot","cooking":"boil","level":"entry"},
        "calories": 40, "protein": 3.0, "fat": 1.5, "carbs": 4.0,
        "materials": [{"name": "嫩豆腐", "quantity": "150g"}, {"name": "海带", "quantity": "10g"}, {"name": "葱花", "quantity": "少许"}],
        "seasonings": [{"name": "白味噌", "quantity": "2汤匙"}, {"name": "柴鱼片", "quantity": "适量"}],
        "steps": [
            "海带提前泡发，切成小片",
            "锅中加水烧开，放入海带煮5分钟出味",
            "豆腐切成1.5cm方块，轻轻放入锅中",
            "转小火，用漏勺将味噌化入汤中（切忌大火沸腾）",
            "撒入葱花和柴鱼片，关火即可",
            "注意：味噌不宜久煮，会失去风味"
        ],
    },
    {
        "name": "黑椒牛排",
        "description": "西餐经典，外焦里嫩，配上浓郁的黑椒汁，是家庭聚餐和节日宴会的首选主菜。掌握火候就能在家做出餐厅水准。",
        "cuisine": "西餐",
        "category": "西餐",
        "tags": {"spicy":"low","temp":"hot","cooking":"grill","level":"hard"},
        "calories": 250, "protein": 26.0, "fat": 15.0, "carbs": 2.0,
        "materials": [{"name": "西冷牛排", "quantity": "200g"}, {"name": "芦笋", "quantity": "5根"}, {"name": "小番茄", "quantity": "3个"}],
        "seasonings": [{"name": "黑胡椒", "quantity": "适量"}, {"name": "海盐", "quantity": "适量"}, {"name": "黄油", "quantity": "20g"}, {"name": "迷迭香", "quantity": "1枝"}, {"name": "蒜瓣", "quantity": "2个"}],
        "steps": [
            "牛排提前30分钟从冰箱取出回温，两面撒海盐和黑胡椒",
            "大火热锅，锅要烧到冒烟",
            "放入牛排，不要翻动，煎2分钟出焦壳",
            "翻面再煎2分钟（中等熟度）",
            "加入黄油、蒜瓣和迷迭香，用勺子淋油",
            "取出牛排静置5分钟，让肉汁均匀分布",
            "锅中余油煎芦笋和小番茄作为配菜"
        ],
    },
]


async def seed_recipes(db: AsyncSession):
    result = await db.execute(select(CustomRecipe).limit(1))
    if result.scalar_one_or_none():
        print("[SEED] 食谱数据已存在，跳过")
        return

    # 查找 admin 用户
    user_q = await db.execute(select(User).where(User.is_admin == True))
    admin = user_q.scalar_one_or_none()
    if not admin:
        user_q = await db.execute(select(User).limit(1))
        admin = user_q.scalar_one_or_none()
    if not admin:
        print("[SEED] 没有用户，跳过食谱种子")
        return

    cat_result = await db.execute(select(FoodCategory))
    cat_map = {c.name: c.id for c in cat_result.scalars().all()}

    count = 0
    for r in SAMPLE_RECIPES:
        # 创建 Food 记录
        food = Food(
            name=r["name"],
            category_id=cat_map.get(r["category"]),
            cuisine=r["cuisine"],
            tags=r["tags"],
            description=r["description"],
            source="seed",
            calories_per_100g=r["calories"],
            protein_per_100g=r["protein"],
            fat_per_100g=r["fat"],
            carbs_per_100g=r["carbs"],
            is_public=True,
        )
        db.add(food)
        await db.flush()

        # 创建 CustomRecipe
        recipe = CustomRecipe(
            user_id=admin.id,
            food_id=food.id,
            cooking_steps=r["steps"],
            is_published=True,
            publish_status="approved",
        )
        db.add(recipe)
        await db.flush()

        # 创建食材
        for m in r["materials"]:
            db.add(CustomRecipeIngredient(
                recipe_id=recipe.id,
                ingredient_name=m["name"],
                quantity=m["quantity"],
                ingredient_type="ingredient",
            ))

        # 创建调料
        for s in r["seasonings"]:
            db.add(CustomRecipeIngredient(
                recipe_id=recipe.id,
                ingredient_name=s["name"],
                quantity=s["quantity"],
                ingredient_type="seasoning",
            ))

        count += 1

    await db.flush()
    print(f"[SEED] 已插入 {count} 个食谱及食材数据")


if __name__ == "__main__":
    async def _main():
        db = async_session()
        try:
            await seed_all(db)
            # 修复 M1：独立运行必须显式 commit，否则仅 flush 的数据全部回滚丢失
            await db.commit()
            print("[SEED] 种子数据已提交")
        finally:
            await db.close()

    asyncio.run(_main())
