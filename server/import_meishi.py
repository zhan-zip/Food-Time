"""美食天下爬虫数据导入数据库

用法: python import_meishi.py
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.food.models import Food, FoodCategory
from src.services.scraper_meishi import scraper_meishi


async def main():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    print("=" * 60)
    print("  食光记 - 美食天下食谱爬虫导入工具")
    print("=" * 60)

    # 1. 爬取（同步，在 async 上下文中直接调用）
    print("\n[1/3] 开始爬取美食天下...")
    recipes = scraper_meishi.scrape(max_pages=50)
    print(f"  爬取完成: {len(recipes)} 条去重食谱")

    if not recipes:
        print("  未获取到任何数据，退出")
        await engine.dispose()
        return

    # 2. 去重
    print("\n[2/3] 检查数据库已有菜品...")
    async with async_session() as session:
        result = await session.execute(select(Food.name))
        existing = {r[0] for r in result.all()}

        new_recipes = [r for r in recipes if r.name not in existing]
        print(f"  数据库中已有: {len(existing)} 条")
        print(f"  待新增: {len(new_recipes)} 条")

        if not new_recipes:
            print("  没有新数据需要导入")
            await engine.dispose()
            return

        # 3. 导入
        print(f"\n[3/3] 导入 {len(new_recipes)} 条新食谱...")

        cat_result = await session.execute(select(FoodCategory))
        categories = {c.name: c.id for c in cat_result.scalars().all()}

        default_cat_names = {"家常菜", "快手菜", "下饭菜", "早餐", "汤羹", "小吃", "烘焙",
                            "猪肉", "鸡肉", "牛肉", "羊肉", "鱼类", "虾类", "蛋类",
                            "蔬菜", "豆制品", "轻食", "素食", "凉菜", "面食", "粥品", "主食",
                            "鸭肉", "零食", "冬季食谱", "夏季食谱", "高颜值", "泡酱腌菜"}
        for cname in default_cat_names:
            if cname not in categories:
                new_cat = FoodCategory(name=cname, icon="", sort_order=99)
                session.add(new_cat)
                await session.flush()
                categories[cname] = new_cat.id

        imported = 0
        skipped_nutrition = 0

        for r in new_recipes:
            try:
                nut = r.nutrition
                cat_id = categories.get(r.category_name) or categories.get("家常菜")

                food = Food(
                    name=r.name,
                    category_id=cat_id,
                    cuisine=r.cuisine,
                    calories_per_100g=nut.get("calories_per_100g"),
                    protein_per_100g=nut.get("protein_per_100g"),
                    fat_per_100g=nut.get("fat_per_100g"),
                    carbs_per_100g=nut.get("carbs_per_100g"),
                    fiber_per_100g=nut.get("fiber_per_100g"),
                    sodium_per_100g=nut.get("sodium_per_100g"),
                    tags={
                        "来源": "美食天下",
                        "菜谱URL": r.source_url,
                        "营养数据来源": nut.get("data_source", "暂无"),
                        "匹配食材": r.ingredients,
                    },
                    source="scraper",
                    source_url=r.source_url,
                    is_public=True,
                )
                session.add(food)
                imported += 1

                if nut.get("calories_per_100g") is None:
                    skipped_nutrition += 1

            except Exception as e:
                print(f"  导入失败 [{r.name}]: {e}")

        await session.commit()

    print(f"\n{'=' * 60}")
    print(f"  导入完成!")
    print(f"  成功导入: {imported} 条")
    print(f"  其中无营养数据: {skipped_nutrition} 条")
    print(f"  数据库总食谱: {len(existing) + imported} 条")
    print(f"{'=' * 60}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
