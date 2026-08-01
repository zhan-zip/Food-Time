"""AI 对话模块 — API 路由（SSE 流式）

路由：
  POST /api/chat/send     — 发送消息，SSE 流式返回
  GET  /api/chat/history  — 获取对话历史
  DELETE /api/chat/history — 清除对话历史
"""

import json
import asyncio

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.database import get_db
from src.dependencies import get_current_user, get_admin_user
from src.auth.models import User
from src.chat.schemas import ChatSendRequest
from src.chat.service import ChatService
from src.chat.models import Conversation
from src.services.deepseek import deepseek
from src.rate_limit import rate_limit

router = APIRouter(prefix="/api/chat", tags=["AI 对话"])


# ============================================================
# SSE 流式对话（主端点）
# ============================================================

@router.post("/send")
@rate_limit("chat", 20, 60, use_user=True)  # H5：AI 对话 20 次/分钟/用户
async def chat_send(
    req: ChatSendRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发送消息，返回 SSE 流式响应。事件类型：tool_start / tool_end / token / done / error"""

    # 快速检查：是否有 API Key
    if not deepseek.is_configured:
        async def error_gen():
            yield _sse("token", {"content": "请在服务端 .env 中配置 DEEPSEEK_API_KEY 后重启"})
            yield _sse("done", {"session_id": req.session_id, "tool_calls": [], "message_id": 0})
        return StreamingResponse(error_gen(), media_type="text/event-stream")

    service = ChatService(db, current_user.id, req.session_id)

    async def stream():
        try:
            async for event in service.run(req.content, req.image_url):
                yield _sse(event["type"], event["data"])
        except asyncio.CancelledError:
            pass  # 客户端断开连接，正常结束
        except Exception as e:
            yield _sse("error", {"message": str(e)})
            # 修复 H1：错误后必须补发 done，否则前端 SSE 等待 done 关闭连接，永久显示"思考中…"
            yield _sse("done", {"session_id": req.session_id, "tool_calls": [], "message_id": 0})

    return StreamingResponse(stream(), media_type="text/event-stream")


# ============================================================
# 对话历史
# ============================================================

@router.get("/history")
async def chat_history(
    session_id: str = "default",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定会话的对话历史"""
    q = (
        select(Conversation)
        .where(
            Conversation.user_id == current_user.id,
            Conversation.session_id == session_id,
        )
        .order_by(Conversation.created_at.asc())
        .limit(100)
    )
    result = await db.execute(q)
    msgs = result.scalars().all()
    return {
        "session_id": session_id,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "tool_name": m.tool_name,
                "created_at": m.created_at.isoformat(),
            }
            for m in msgs
        ],
    }


@router.delete("/history")
async def clear_history(
    session_id: str = "default",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """清除指定会话的对话历史"""
    await db.execute(
        delete(Conversation).where(
            Conversation.user_id == current_user.id,
            Conversation.session_id == session_id,
        )
    )
    await db.commit()
    return {"message": "已清除", "session_id": session_id}


# ============================================================
# 向量索引（管理端）
# ============================================================

@router.post("/build-rag-index")
async def build_rag_index(
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """重建食物 RAG 索引。需要管理员权限"""
    from sqlalchemy import text
    result = await db.execute(text("SELECT id, name, cuisine, category_id, calories_per_100g, tags FROM foods"))
    rows = result.fetchall()

    # 同时获取分类名
    cat_result = await db.execute(text("SELECT id, name FROM food_categories"))
    cat_map = {row[0]: row[1] for row in cat_result.fetchall()}

    foods = []
    for row in rows:
        cat_name = cat_map.get(row[3], "")
        foods.append({
            "id": row[0],
            "name": row[1],
            "cuisine": row[2] or "",
            "category_id": row[3] or "",
            "category_name": cat_name,
            "calories_per_100g": str(row[4]) if row[4] else "",
            "tags": row[5] or "[]",
        })

    from src.services.vector_store import vector_store
    await vector_store.build_index(foods, deepseek.embed)

    return {"message": "RAG 索引重建完成", "count": len(foods)}


# ============================================================
# 工具
# ============================================================

def _sse(event_type: str, data: dict) -> str:
    """格式化为 SSE 事件字符串"""
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
