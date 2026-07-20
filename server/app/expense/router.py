"""记账模块 - API 路由"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/expense", tags=["记账"])


@router.get("/records")
async def expense_records():
    """查询账单（P1 实现）"""
    return {"items": [], "total": 0}


@router.get("/stats")
async def expense_stats():
    """账单统计数据（P1 实现）"""
    return {
        "total_month": 0,
        "categories": {},
        "daily_trend": [],
    }
