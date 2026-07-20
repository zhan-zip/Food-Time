"""饮食记录模块 - API 路由"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/diet", tags=["饮食记录"])


@router.get("/records")
async def diet_records():
    """查询饮食记录（P1 实现）"""
    return {"items": [], "total": 0}


@router.get("/preferences")
async def preferences():
    """获取偏好分析（P1 实现）"""
    return {
        "spicy_level": 0,
        "sweet_level": 0,
        "hot_cold_ratio": 0.5,
        "fav_cuisines": {},
        "fav_tags": {},
    }


@router.get("/nutrition")
async def nutrition():
    """获取营养分析数据（P1 实现）"""
    return {
        "days": [],
        "avg_calories": 0,
        "avg_protein": 0,
        "avg_fat": 0,
        "avg_carbs": 0,
    }
