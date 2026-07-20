"""管理员模块 - API 路由"""

from fastapi import APIRouter, Depends
from app.dependencies import get_admin_user
from app.auth.models import User

router = APIRouter(prefix="/api/admin", tags=["管理员"])


@router.get("/stats")
async def admin_stats(current_user: User = Depends(get_admin_user)):
    """平台数据统计"""
    return {
        "users": 0,
        "foods": 0,
        "recipes": 0,
    }
