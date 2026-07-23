"""公共食物广场模块 - API 路由"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/public", tags=["公共广场"])


@router.get("/recipes")
async def browse_recipes(page: int = 1, page_size: int = 20):
    """浏览食谱列表（P1 实现）"""
    return {"items": [], "total": 0, "page": page, "page_size": page_size}
