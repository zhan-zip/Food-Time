"""下厨房食谱爬虫 + 营养估算

数据流程：
1. 爬取下厨房分类+热门页面获取菜名和分类
2. 从菜名中匹配 NUTRITION_REF 中的已知食材
3. 基于食材营养参考表加权估算每100g营养
4. 写入数据库，标注数据来源

数据来源标注：
- 菜名/分类 → 下厨房 (www.xiachufang.com)
- 营养数据 → 中国食物成分表（第六版），中国疾病预防控制中心营养与健康所
"""

import re
import json
import asyncio
import random
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup

from src.services.nutrition_ref import NUTRITION_REF

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# 下厨房分类 → 我们的 category_id 映射
CATEGORY_MAP = {
    "家常菜": ("家常菜", "chinese"),
    "快手菜": ("快手菜", "chinese"),
    "下饭菜": ("下饭菜", "chinese"),
    "早餐": ("早餐", "chinese"),
    "汤羹": ("汤羹", "chinese"),
    "小吃": ("小吃", "chinese"),
    "烘焙": ("烘焙", "western"),
    "猪肉": ("猪肉", "chinese"),
    "鸡肉": ("鸡肉", "chinese"),
    "牛肉": ("牛肉", "chinese"),
    "羊肉": ("羊肉", "chinese"),
    "鱼": ("鱼类", "chinese"),
    "虾": ("虾类", "chinese"),
    "鸡蛋": ("蛋类", "chinese"),
    "土豆": ("蔬菜", "chinese"),
    "豆腐": ("豆制品", "chinese"),
    "茄子": ("蔬菜", "chinese"),
    "排骨": ("猪肉", "chinese"),
    "减肥": ("轻食", "chinese"),
    "素菜": ("素食", "chinese"),
    "凉菜": ("凉菜", "chinese"),
    "面": ("面食", "chinese"),
    "粥": ("粥品", "chinese"),
    "炒饭": ("主食", "chinese"),
}

# 食材关键词 → NUTRITION_REF key 的模糊匹配表
INGREDIENT_ALIAS = {
    "鸡蛋": "鸡蛋（白壳）", "蛋": "鸡蛋（白壳）", "鸭蛋": "鸭蛋",
    "猪肉": "猪肉（肥瘦）", "瘦肉": "猪肉（瘦）", "五花肉": "猪肉（肥瘦）",
    "猪排骨": "猪排骨", "排骨": "猪排骨", "猪蹄": "猪蹄",
    "牛肉": "牛肉（肥瘦）", "牛腩": "牛腩", "牛腱": "牛腱子",
    "羊肉": "羊肉（肥瘦）", "鸡肉": "鸡肉（鸡胸肉）", "鸭肉": "鸭肉",
    "鸡胸": "鸡肉（鸡胸肉）", "鸡腿": "鸡肉（鸡腿肉）", "鸭": "鸭肉", "鸭肉": "鸭肉",
    "鱼": "草鱼", "草鱼": "草鱼", "鲤鱼": "鲤鱼", "鲫鱼": "鲫鱼",
    "鲈鱼": "鲈鱼", "带鱼": "带鱼", "鳕鱼": "鳕鱼", "三文鱼": "三文鱼",
    "虾": "虾（对虾）", "虾仁": "虾仁", "蟹": "蟹（大闸蟹）", "蛤蜊": "蛤蜊",
    "白菜": "大白菜", "青菜": "油菜", "油菜": "油菜", "菠菜": "菠菜",
    "生菜": "生菜", "芹菜": "芹菜", "韭菜": "韭菜", "空心菜": "空心菜",
    "西兰花": "西兰花", "花菜": "花椰菜", "番茄": "番茄", "西红柿": "番茄",
    "黄瓜": "黄瓜", "茄子": "茄子", "土豆": "马铃薯", "马铃薯": "马铃薯",
    "胡萝卜": "胡萝卜", "白萝卜": "白萝卜", "冬瓜": "冬瓜", "南瓜": "南瓜",
    "苦瓜": "苦瓜", "丝瓜": "丝瓜", "豆角": "豇豆", "四季豆": "四季豆",
    "青椒": "青椒", "辣椒": "青椒", "洋葱": "洋葱",
    "山药": "山药", "莲藕": "莲藕", "芋头": "芋头",
    "豆腐": "豆腐（北豆腐）", "豆浆": "豆浆", "腐竹": "腐竹", "豆腐皮": "豆腐皮",
    "黄豆": "黄豆", "绿豆": "绿豆", "豆芽": "豆芽（绿豆芽）",
    "牛奶": "牛奶（全脂）", "酸奶": "酸奶（原味）", "奶酪": "奶酪",
    "香菇": "香菇（鲜）", "金针菇": "金针菇", "木耳": "木耳（黑木耳，鲜）",
    "口蘑": "口蘑",
    "米饭": "米饭（蒸）", "大米": "大米（籼米）", "面条": "面条（煮）",
    "馒头": "馒头（标准粉）", "面粉": "小麦粉（标准粉）",
    "小米": "小米", "玉米": "玉米（鲜）", "红薯": "红薯", "糯米": "糯米",
    "苹果": "苹果", "香蕉": "香蕉", "橙子": "橙子", "葡萄": "葡萄",
    "西瓜": "西瓜", "梨": "梨", "草莓": "草莓",
    "酱油": "酱油（生抽）", "醋": "醋（陈醋）", "蚝油": "蚝油", "盐": "食盐",
    "油": "花生油", "花生油": "花生油", "豆瓣酱": "豆瓣酱",
    "糖": "白糖", "白糖": "白糖",
    "火腿": "火腿肠", "火腿肠": "火腿肠", "腊肉": "腊肉",
}


@dataclass
class RecipeData:
    name: str
    category_name: str
    cuisine: str
    ingredients: list[str]
    nutrition: dict  # per 100g
    source_url: str


class XiaChuFangScraper:
    """下厨房食谱爬虫"""

    BASE = "https://www.xiachufang.com"

    def __init__(self):
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=30,
                follow_redirects=True,
                headers={"User-Agent": random.choice(USER_AGENTS)},
            )
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def scrape_category(self, category_name: str, category_url: str, max_pages: int = 3) -> list[RecipeData]:
        """爬取一个分类下的菜谱列表"""
        client = await self._get_client()
        results = []

        for page in range(1, max_pages + 1):
            url = f"{self.BASE}{category_url}"
            if page > 1:
                url = f"{self.BASE}{category_url}?page={page}"
            try:
                resp = await client.get(url)
                if resp.status_code != 200:
                    break
                soup = BeautifulSoup(resp.text, "lxml")
                recipe_links = soup.select('a[href*="/recipe/"]')
                for a in recipe_links:
                    name = a.get_text(strip=True)
                    href = a.get("href", "")
                    if not name or not href or "/recipe/" not in href:
                        continue
                    # 过滤掉非菜名链接（如用户头像、评论等）
                    if len(name) < 2 or len(name) > 30:
                        continue

                    cat, cuisine = CATEGORY_MAP.get(category_name, (category_name, "chinese"))
                    ingredients = self._extract_ingredients(name)
                    nutrition = self._estimate_nutrition(ingredients)

                    results.append(RecipeData(
                        name=name,
                        category_name=cat,
                        cuisine=cuisine,
                        ingredients=ingredients,
                        nutrition=nutrition,
                        source_url=f"{self.BASE}{href}",
                    ))

                # 如果页面上没有菜谱链接了，说明到底了
                if not recipe_links:
                    break

                # 礼貌延迟
                await asyncio.sleep(random.uniform(0.3, 0.8))

            except Exception as e:
                print(f"[Scraper] {url} 失败: {e}")
                break

        return results

    async def scrape_explore(self, max_pages: int = 10) -> list[RecipeData]:
        """爬取热门探索页面"""
        client = await self._get_client()
        results = []

        for page in range(1, max_pages + 1):
            url = f"{self.BASE}/explore/"
            if page > 1:
                url = f"{self.BASE}/explore/?page={page}"
            try:
                resp = await client.get(url)
                if resp.status_code != 200:
                    break
                soup = BeautifulSoup(resp.text, "lxml")
                recipe_links = soup.select('a[href*="/recipe/"]')

                page_results = 0
                for a in recipe_links:
                    name = a.get_text(strip=True)
                    href = a.get("href", "")
                    if not name or not href or len(name) < 2 or len(name) > 30:
                        continue
                    # 尝试从链接或上下文推断分类
                    cat = self._guess_category(name)
                    ingredients = self._extract_ingredients(name)
                    nutrition = self._estimate_nutrition(ingredients)

                    results.append(RecipeData(
                        name=name,
                        category_name=cat,
                        cuisine="chinese",
                        ingredients=ingredients,
                        nutrition=nutrition,
                        source_url=f"{self.BASE}{href}",
                    ))
                    page_results += 1

                if page_results == 0:
                    break
                await asyncio.sleep(random.uniform(0.3, 0.8))

            except Exception as e:
                print(f"[Scraper] {url} 失败: {e}")
                break

        return results

    async def scrape_all(self) -> list[RecipeData]:
        """爬取所有分类 + 热门"""
        all_recipes: list[RecipeData] = []
        seen_names = set()

        # 0. 先获取分类 ID 映射
        cat_id_map = await self._get_category_ids()

        # 1. 爬取热门
        print("[Scraper] 爬取热门菜谱...")
        explore = await self.scrape_explore(max_pages=15)
        for r in explore:
            if r.name not in seen_names:
                seen_names.add(r.name)
                all_recipes.append(r)
        print(f"[Scraper] 热门: {len(explore)} 条 (去重后 {len(all_recipes)})")

        # 2. 爬取每个分类
        for cat_name, (cat_label, cuisine) in CATEGORY_MAP.items():
            if len(all_recipes) >= 500:
                break
            cat_id = cat_id_map.get(cat_name)
            if not cat_id:
                continue
            print(f"[Scraper] 爬取分类: {cat_name} (ID:{cat_id})...")
            cat_recipes = await self.scrape_category(cat_label, f"/category/{cat_id}/", max_pages=2)
            for r in cat_recipes:
                if r.name not in seen_names:
                    seen_names.add(r.name)
                    all_recipes.append(r)
            await asyncio.sleep(random.uniform(1, 2))

        await self.close()
        print(f"[Scraper] 总计: {len(all_recipes)} 条去重食谱")
        return all_recipes[:500]

    async def _get_category_ids(self) -> dict[str, str]:
        """从分类页面提取 分类名 → 数字ID 的映射"""
        client = await self._get_client()
        try:
            resp = await client.get(f"{self.BASE}/category/")
            soup = BeautifulSoup(resp.text, "lxml")
            links = soup.select('a[href*="/category/"]')
            mapping = {}
            for a in links:
                href = a.get("href", "")
                text = a.get_text(strip=True)
                # URL 格式: /category/40076/
                match = re.search(r'/category/(\d+)/?', href)
                if match and text and text in CATEGORY_MAP:
                    mapping[text] = match.group(1)
            print(f"[Scraper] 分类ID映射: {len(mapping)} 个")
            return mapping
        except Exception as e:
            print(f"[Scraper] 获取分类ID失败: {e}")
            return {}

    # ===========================================================
    # 食材提取
    # ===========================================================
    def _extract_ingredients(self, name: str) -> list[str]:
        """从菜名中提取已知食材"""
        found = []
        # 按长度降序匹配（优先长词，避免"鸡蛋"匹配到"鸡"）
        sorted_keys = sorted(INGREDIENT_ALIAS.keys(), key=len, reverse=True)
        for kw in sorted_keys:
            if kw in name:
                ref_key = INGREDIENT_ALIAS[kw]
                if ref_key not in found and ref_key in NUTRITION_REF:
                    found.append(ref_key)
        return found

    # ===========================================================
    # 营养估算
    # ===========================================================
    def _estimate_nutrition(self, ingredients: list[str]) -> dict:
        """基于食材营养参考表加权估算。

        方法：对每种食材取 NUTRITION_REF 中的每100g营养值，
        等权平均（假设各食材用量大致相当）。
        调料类不计入主营养素估算（热量贡献忽略），但标注钠含量提醒。
        """
        if not ingredients:
            return self._empty_nutrition()

        # 分离主料和调料
        seasonings = {"酱油", "醋", "蚝油", "食盐", "味精", "鸡精", "料酒",
                      "豆瓣酱", "甜面酱", "辣椒酱", "番茄酱", "白砂糖", "冰糖",
                      "花生油", "猪油", "橄榄油", "菜籽油", "香油", "花椒油",
                      "八角", "花椒", "桂皮", "白胡椒粉", "淀粉", "葱油"}

        mains = [i for i in ingredients if i not in seasonings]
        if not mains:
            mains = ingredients  # fallback

        total = {"calories": 0, "protein": 0, "fat": 0,
                 "carbs": 0, "fiber": 0, "sodium": 0}
        count = len(mains)

        for ing in mains:
            nd = NUTRITION_REF.get(ing, {})
            total["calories"] += nd.get("calories", 0)
            total["protein"] += nd.get("protein", 0)
            total["fat"] += nd.get("fat", 0)
            total["carbs"] += nd.get("carbs", 0)
            total["fiber"] += nd.get("fiber", 0)
            total["sodium"] += nd.get("sodium", 0)

        # 平均值（per 100g混合食材）
        result = {
            "calories_per_100g": round(total["calories"] / count, 1),
            "protein_per_100g": round(total["protein"] / count, 1),
            "fat_per_100g": round(total["fat"] / count, 1),
            "carbs_per_100g": round(total["carbs"] / count, 1),
            "fiber_per_100g": round(total["fiber"] / count, 1),
            "sodium_per_100g": round(total["sodium"] / count, 1),
            "data_source": "中国食物成分表（第六版）- 基于食材加权估算",
        }
        return result

    @staticmethod
    def _empty_nutrition() -> dict:
        return {
            "calories_per_100g": None,
            "protein_per_100g": None,
            "fat_per_100g": None,
            "carbs_per_100g": None,
            "fiber_per_100g": None,
            "sodium_per_100g": None,
            "data_source": None,
        }

    @staticmethod
    def _guess_category(name: str) -> str:
        """从菜名猜测分类"""
        cat_keywords = {
            "汤": "汤羹", "羹": "汤羹", "粥": "粥品", "面": "面食",
            "饼": "面食", "饭": "主食", "炒饭": "主食", "包子": "面食",
            "饺子": "面食", "馒头": "面食", "蛋糕": "烘焙", "面包": "烘焙",
            "烤": "烘焙", "拌": "凉菜", "凉": "凉菜", "沙拉": "轻食",
            "鸡": "鸡肉", "鸭": "鸭肉", "鱼": "鱼类", "虾": "虾类",
            "肉": "猪肉", "排骨": "猪肉", "牛": "牛肉", "羊": "羊肉",
            "蛋": "蛋类", "豆腐": "豆制品", "素": "素食",
        }
        for kw, cat in cat_keywords.items():
            if kw in name:
                return cat
        return "家常菜"


# 全局实例
scraper = XiaChuFangScraper()
