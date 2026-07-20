"""AI 对话模块 - API 路由"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/chat", tags=["AI 对话"])


@router.get("/history/{session_id}")
async def chat_history(session_id: str):
    """获取对话历史（P1 实现）"""
    return {"session_id": session_id, "messages": []}


@router.delete("/history/{session_id}")
async def clear_history(session_id: str):
    """清除对话历史"""
    return {"message": "已清除", "session_id": session_id}
