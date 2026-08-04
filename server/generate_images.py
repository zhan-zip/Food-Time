"""
AI 菜品配图批量生成脚本（SiliconFlow kwai-kolors/kolors）

用法：
  python generate_images.py                     # 广场已审核菜谱
  python generate_images.py --top 100           # 食物库前 N 个干净菜名（按分类优先级 + 短名）
  python generate_images.py 番茄炒蛋 宫保鸡丁     # 指定菜名

产物：server/static/food_img/{菜名}.png（已存在则跳过，幂等）
"""
import asyncio
import pathlib
import re
import sys

import httpx
from openai import AsyncOpenAI, RateLimitError

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from src.config import settings  # noqa: E402

IMG_DIR = pathlib.Path(__file__).parent / "static" / "food_img"
IMG_DIR.mkdir(parents=True, exist_ok=True)

# 明显不适合当 prompt/文件名的爬虫网络标题词
_NOISE_WORDS = [
    "巨巨", "下饭", "无敌", "绝了", "上瘾", "掉称", "拿肉", "比布丁",
    "超开胃", "香糯", "老少皆宜", "手撕", "零失败", "神仙", "太太太",
    "好吃到", "舔盘", "抢着吃", "断货", "一次就", "忍不住", "快手",
    "简单", "做法", "秘制", "家常",
]

# 偏门/非主菜类词（饮品/甜品/酱糊/茶类，用户很少在 TodayEat 搜，优先排除）
_SIDELINE_WORDS = [
    "茶", "奶冻", "冻撞奶", "糊", "酱", "蜜", "冻", "酪", "饮",
    "雪燕", "花胶", "汁", "卷", "糕", "曲奇", "吐司", "布丁",
    "奶昔", "酸奶", "凉茶", "果酱", "花生",
]

# 食物库分类优先级（高频常见分类靠前）
_CATEGORY_PRIORITY = [
    "家常菜", "面食", "猪肉", "汤羹", "鸡肉", "主食", "凉菜",
    "虾类", "快手菜", "早餐", "牛肉", "烘焙", "鱼类", "蛋类",
    "粥品", "豆制品", "鸭肉", "川菜", "素食", "轻食",
]


def safe_name(name: str) -> str:
    """文件名字符清洗：去掉路径特殊字符与空白"""
    return re.sub(r'[\\/:*?"<>|\s]+', "_", name).strip()


def is_clean(name: str) -> bool:
    """判断菜名是否适合作为生成 prompt 与文件名（过滤爬虫噪音标题）"""
    s = name.strip()
    if not (2 <= len(s) <= 12):
        return False
    if re.search(r"[←-⟿\U0001f000-\U0001ffff!！?？]", s):
        return False
    if re.search(r"[A-Za-z]", s):
        return False
    if any(w in s for w in _NOISE_WORDS):
        return False
    if any(w in s for w in _SIDELINE_WORDS):
        return False
    # 词尾排除：饮品/膏类/干果/食疗方/装饰菜
    if s.endswith(("水", "膏", "方", "干", "花朵", "挞", "球")):
        return False
    # 明显甜点/装饰/繁体错字/杂项
    if any(w in s for w in [
        "雪媚娘", "青团", "糖渍", "双色", "玫瑰花", "魚", "木薯",
        "桃胶", "石斛", "沙葛", "艾糍", "糖水", "气泡", "渍水果",
        "乳鸽", "蚕蛹", "鸵鸟", "燕窝",
    ]):
        return False
    return True


def build_prompt(name: str) -> str:
    return (
        f"一盘精致的「{name}」，专业美食摄影，俯拍视角，"
        "暖色调灯光，摆盘精美，白色陶瓷餐盘，餐桌背景，"
        "食材清晰有食欲，高清美食大片"
    )


async def generate_one(
    client: AsyncOpenAI, name: str, max_retries: int = 5
) -> bool:
    fname = safe_name(name)
    out = IMG_DIR / f"{fname}.png"
    if out.exists():
        print(f"[跳过] {name} 已存在")
        return True
    for attempt in range(max_retries):
        try:
            resp = await client.images.generate(
                model=settings.IMG_GEN_MODEL,
                prompt=build_prompt(name),
                size="1024x1024",
                n=1,
            )
            url = resp.data[0].url
            async with httpx.AsyncClient(timeout=120) as hc:
                r = await hc.get(url)
                if r.status_code == 200 and r.content:
                    out.write_bytes(r.content)
                    print(f"[OK] {name} -> {out.name} ({len(r.content) // 1024}KB)")
                    return True
                print(f"[失败] {name} 下载状态码 {r.status_code}")
                return False
        except RateLimitError as e:
            # SiliconFlow IPM 限流：等待 60s 后重试
            print(f"[限流] {name} 429，等待 60s 重试 ({attempt + 1}/{max_retries})")
            await asyncio.sleep(60)
        except Exception as e:
            print(f"[失败] {name}: {type(e).__name__}: {str(e)[:120]}")
            return False
    print(f"[放弃] {name} 重试 {max_retries} 次仍被限流")
    return False


async def load_square_names() -> list:
    """读取广场已审核菜谱的菜名"""
    from sqlalchemy import select

    from src.custom_food.models import CustomRecipe
    from src.database import async_session
    from src.food.models import Food

    async with async_session() as db:
        rows = await db.execute(
            select(Food.name)
            .join(CustomRecipe, CustomRecipe.food_id == Food.id)
            .where(
                CustomRecipe.is_published.is_(True),
                CustomRecipe.publish_status == "approved",
            )
        )
        return list(rows.scalars())


async def load_candidates(limit: int) -> list:
    """从食物库取前 N 个干净菜名（分类优先级 + 短名优先），跳过已生成的"""
    from sqlalchemy import select

    from src.database import async_session
    from src.food.models import Food, FoodCategory

    existing = {p.stem for p in IMG_DIR.glob("*.png")}
    async with async_session() as db:
        rows = await db.execute(
            select(Food.name, FoodCategory.name.label("cat"), Food.source)
            .join(FoodCategory, Food.category_id == FoodCategory.id)
            .where(Food.is_public.is_(True))
        )
        items = []
        for name, cat, source in rows.all():
            if not is_clean(name):
                continue
            if safe_name(name) in existing:
                continue
            # seed（人工精选）优先 → 分类优先级 → 长度 3-8 适中 → 名称
            src_pri = 0 if source == "seed" else 1
            cat_pri = _CATEGORY_PRIORITY.index(cat) if cat in _CATEGORY_PRIORITY else len(_CATEGORY_PRIORITY)
            len_pen = 0 if 3 <= len(name) <= 8 else 1
            items.append((src_pri, cat_pri, len_pen, name))
        items.sort()
        return [n for *_, n in items[:limit]]


async def main(names: list) -> None:
    if not settings.IMG_GEN_API_KEY:
        print("错误：IMG_GEN_API_KEY 未配置（server/.env）")
        return
    if not names:
        print("没有可生成的菜谱名")
        return
    client = AsyncOpenAI(
        api_key=settings.IMG_GEN_API_KEY, base_url=settings.IMG_GEN_BASE_URL
    )
    ok = 0
    for name in names:
        if await generate_one(client, name):
            ok += 1
        # 拉大请求间隔，避免触发 SiliconFlow IPM（每分钟请求数）限流
        await asyncio.sleep(15)
    print(f"\n完成：成功 {ok}/{len(names)}，输出目录 {IMG_DIR}")


if __name__ == "__main__":
    args = sys.argv[1:]
    top = None
    if "--top" in args:
        i = args.index("--top")
        try:
            top = int(args[i + 1])
        except (IndexError, ValueError):
            top = None
        del args[i:i + 2]

    if args:
        names = args
    elif top:
        names = asyncio.run(load_candidates(top))
        print(f"已筛选 {len(names)} 个菜名（前 {top} 名，按分类优先级）")
    else:
        names = asyncio.run(load_square_names())
    asyncio.run(main(names))
