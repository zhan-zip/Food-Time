"""自定义食物模块 - API 路由"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/custom", tags=["自定义食物"])


@router.get("/my")
async def my_recipes():
    """我的自定义食谱列表（P1 实现）"""
    return {"items": [], "total": 0}
