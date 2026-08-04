"""AI 菜品图生成服务（SiliconFlow kwai-kolors/kolors）

供 custom_food 保存菜谱时后台自动生成配图，产物与 generate_images.py 一致：
    server/static/food_img/{菜名}.png
"""
import pathlib
import re

import httpx
from openai import AsyncOpenAI

from src.config import settings

IMG_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "static" / "food_img"
_PROMPT = (
    "一盘精致的「{name}」，专业美食摄影，俯拍视角，"
    "暖色调灯光，摆盘精美，白色陶瓷餐盘，餐桌背景，"
    "食材清晰有食欲，高清美食大片"
)


def safe_name(name: str) -> str:
    """与 generate_images.py safe_name 保持一致的文件名清洗"""
    return re.sub(r'[\\/:*?"<>|\s]+', "_", name).strip()


def is_configured() -> bool:
    return bool(settings.IMG_GEN_API_KEY and settings.IMG_GEN_BASE_URL)


async def generate_and_save(name: str) -> bool:
    """生成一张菜谱 AI 图并保存；已存在则跳过；失败静默返回 False（不抛异常）。"""
    if not name or not is_configured():
        return False
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    out = IMG_DIR / f"{safe_name(name)}.png"
    if out.exists():
        return True
    try:
        client = AsyncOpenAI(
            api_key=settings.IMG_GEN_API_KEY, base_url=settings.IMG_GEN_BASE_URL
        )
        resp = await client.images.generate(
            model=settings.IMG_GEN_MODEL,
            prompt=_PROMPT.format(name=name),
            size="1024x1024",
            n=1,
        )
        url = resp.data[0].url
        async with httpx.AsyncClient(timeout=120) as hc:
            r = await hc.get(url)
            if r.status_code == 200 and r.content:
                out.write_bytes(r.content)
                return True
    except Exception:
        return False
    return False
