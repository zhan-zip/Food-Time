"""美食天下食谱爬虫

数据来源: home.meishichina.com
列表页: /recipe-list.html?page=N (每页10条)
分类页: /recipe/{category_slug}/?page=N

使用 curl_cffi 模拟浏览器绕过 Cloudflare 防护。
"""

import re
import time
import random
from dataclasses import dataclass

from curl_cffi import requests as cffi_requests
from bs4 import BeautifulSoup

from src.services.nutrition_ref import NUTRITION_REF
from src.services.scraper import INGREDIENT_ALIAS

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]

CATEGORY_SLUGS = {
    "kuaishoucai": "快手菜", "zaocan": "早餐", "hongbei": "烘焙",
    "liangcai": "凉菜", "tang": "汤羹", "xiaochi": "小吃",
    "mian": "面食", "zhushi": "主食", "sucai": "素菜",
    "shala": "轻食", "zhou": "粥品", "xiafancai": "下饭菜",
    "jiachangcai": "家常菜", "dongji": "冬季食谱", "xiaji": "夏季食谱",
}


@dataclass
class RecipeData:
    name: str
    category_name: str
    cuisine: str
    ingredients: list[str]
    nutrition: dict
    source_url: str


# ============ 共享营养估算逻辑 ============

def _extract_ingredients_from_name(name: str) -> list[str]:
    found = []
    sorted_keys = sorted(INGREDIENT_ALIAS.keys(), key=len, reverse=True)
    for kw in sorted_keys:
        if kw in name:
            ref_key = INGREDIENT_ALIAS[kw]
            if ref_key not in found and ref_key in NUTRITION_REF:
                found.append(ref_key)
    return found


def _match_ingredient(text: str) -> str | None:
    for alias, ref_key in INGREDIENT_ALIAS.items():
        if alias in text:
            return ref_key
    for key in NUTRITION_REF:
        if key in text or text in key:
            return key
    return None


def _estimate_nutrition(ingredients: list[str]) -> dict:
    if not ingredients:
        return {
            "calories_per_100g": None, "protein_per_100g": None,
            "fat_per_100g": None, "carbs_per_100g": None,
            "fiber_per_100g": None, "sodium_per_100g": None,
            "data_source": None,
        }
    seasonings = {"酱油", "醋", "蚝油", "食盐", "味精", "鸡精", "料酒",
                  "豆瓣酱", "甜面酱", "辣椒酱", "番茄酱", "白砂糖", "冰糖",
                  "花生油", "猪油", "橄榄油", "菜籽油", "香油", "花椒油",
                  "八角", "花椒", "桂皮", "白胡椒粉", "淀粉", "葱油"}
    mains = [i for i in ingredients if i not in seasonings]
    if not mains:
        mains = ingredients
    total = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0, "fiber": 0, "sodium": 0}
    count = len(mains)
    for ing in mains:
        nd = NUTRITION_REF.get(ing, {})
        total["calories"] += nd.get("calories", 0)
        total["protein"] += nd.get("protein", 0)
        total["fat"] += nd.get("fat", 0)
        total["carbs"] += nd.get("carbs", 0)
        total["fiber"] += nd.get("fiber", 0)
        total["sodium"] += nd.get("sodium", 0)
    return {
        "calories_per_100g": round(total["calories"] / count, 1),
        "protein_per_100g": round(total["protein"] / count, 1),
        "fat_per_100g": round(total["fat"] / count, 1),
        "carbs_per_100g": round(total["carbs"] / count, 1),
        "fiber_per_100g": round(total["fiber"] / count, 1),
        "sodium_per_100g": round(total["sodium"] / count, 1),
        "data_source": "中国食物成分表（第六版）- 基于食材加权估算",
    }


def _guess_category(name: str) -> str:
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


# ============ 爬虫主体 ============

class MeiShiScraper:
    BASE = "https://home.meishichina.com"

    def _fetch(self, url: str) -> BeautifulSoup | None:
        """发送请求并返回 BeautifulSoup"""
        try:
            resp = cffi_requests.get(
                url,
                impersonate="chrome120",
                headers={
                    "User-Agent": random.choice(USER_AGENTS),
                    "Accept-Language": "zh-CN,zh;q=0.9",
                },
                timeout=30,
            )
            if resp.status_code != 200:
                return None
            return BeautifulSoup(resp.text, "lxml")
        except Exception as e:
            print(f"[MeiShi] 请求失败 {url}: {e}")
            return None

    def _parse_list_page(self, soup: BeautifulSoup, cat_name: str) -> list[RecipeData]:
        """解析列表页，提取所有食谱

        结构: div.detail > h2 > a (菜名+链接) + 文本(原料：... N人收藏)
        """
        results = []
        detail_divs = soup.select('div.detail')
        if not detail_divs:
            # 尝试备选选择器
            detail_divs = soup.select('[class*="detail"]')

        for div in detail_divs:
            # 提取菜名和URL
            name_a = div.select_one('h2 a[href*="/recipe-"]')
            if not name_a:
                name_a = div.select_one('a[href*="/recipe-"]')
                if not name_a:
                    continue

            name = name_a.get_text(strip=True)
            href = name_a.get("href", "")
            if len(name) < 2 or len(name) > 35:
                continue

            # 提取原料
            div_text = div.get_text(" ", strip=True)
            ing_match = re.search(r'原料[：:]\s*(.+?)\s*(\d+)人收藏', div_text)
            raw_ingredients = []
            if ing_match:
                raw_text = ing_match.group(1).strip().rstrip("。，, ")
                raw_ingredients = [i.strip() for i in re.split(r'[、，,]', raw_text) if i.strip()]

            # 匹配已知食材
            ingredients = self._extract_ingredients_from_raw(raw_ingredients, name)
            nutrition = _estimate_nutrition(ingredients)

            full_url = f"{self.BASE}{href}" if href.startswith("/") else href
            results.append(RecipeData(
                name=name,
                category_name=cat_name,
                cuisine="chinese",
                ingredients=ingredients,
                nutrition=nutrition,
                source_url=full_url,
            ))

        return results

    def _extract_ingredients_from_raw(self, raw_list: list[str], name: str) -> list[str]:
        """从页面原料文本 + 菜名中匹配已知食材"""
        found = []
        for raw in raw_list:
            # 清理量词、品牌等
            clean = re.sub(
                r'[约半\d]+克?[gG克]?|少许|适量|若干|个|根|条|勺|汤匙|茶匙'
                r'|毫升|ml|ML|轻盐|特级|原汁|六月鲜|等|\([^)]*\)|（[^）]*）',
                '', raw
            ).strip()
            if len(clean) < 2:
                continue
            ref_key = _match_ingredient(clean)
            if ref_key and ref_key not in found:
                found.append(ref_key)
        # 补充菜名提取
        for ing in _extract_ingredients_from_name(name):
            if ing not in found:
                found.append(ing)
        return found

    def scrape(self, max_pages: int = 50) -> list[RecipeData]:
        """爬取综合列表 + 分类补充"""
        results: list[RecipeData] = []
        seen_names = set()
        blocked_pages = 0

        # 1. 综合列表
        print("[MeiShi] 爬取综合列表...")
        for page in range(1, max_pages + 1):
            if len(results) >= 500 or blocked_pages >= 3:
                break

            url = f"{self.BASE}/recipe-list.html"
            if page > 1:
                url = f"{self.BASE}/recipe-list.html?page={page}"

            soup = self._fetch(url)
            if soup is None:
                blocked_pages += 1
                continue
            blocked_pages = 0  # reset on success

            page_data = self._parse_list_page(soup, _guess_category(""))
            page_added = 0
            for r in page_data:
                if r.name not in seen_names:
                    seen_names.add(r.name)
                    r.category_name = _guess_category(r.name)
                    results.append(r)
                    page_added += 1

            print(f"[MeiShi] 第{page}页: +{page_added} 条 (累计{len(results)})")
            if page_added == 0:
                break
            time.sleep(random.uniform(1.5, 3.0))

        # 2. 分类补充
        print(f"\n[MeiShi] 综合列表: {len(results)} 条，爬分类补充...")
        for slug, cat_name in CATEGORY_SLUGS.items():
            if len(results) >= 550 or blocked_pages >= 3:
                break

            for page in range(1, 4):
                url = f"{self.BASE}/recipe/{slug}/"
                if page > 1:
                    url = f"{self.BASE}/recipe/{slug}/?page={page}"

                soup = self._fetch(url)
                if soup is None:
                    blocked_pages += 1
                    break

                page_data = self._parse_list_page(soup, cat_name)
                for r in page_data:
                    if r.name not in seen_names:
                        seen_names.add(r.name)
                        results.append(r)

                time.sleep(random.uniform(1.5, 3.0))

        print(f"[MeiShi] 总计: {len(results)} 条去重食谱")
        return results[:550]


scraper_meishi = MeiShiScraper()
