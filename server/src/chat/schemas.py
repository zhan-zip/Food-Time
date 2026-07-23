"""AI 对话 Pydantic 模型 — 请求/响应/SSE 事件"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ============================================================
# 请求
# ============================================================

class ChatSendRequest(BaseModel):
    """发送消息请求"""
    content: str = Field(..., description="用户消息文本")
    session_id: str = Field(default="default", description="会话ID，同一会话保持上下文")
    image_url: Optional[str] = Field(default=None, description="附带图片URL（可选，用于食物识别）")


class ChatHistoryRequest(BaseModel):
    """获取历史请求"""
    session_id: str = Field(default="default")


# ============================================================
# 响应
# ============================================================

class ChatMessage(BaseModel):
    """单条消息"""
    id: int
    role: str
    content: str
    tool_name: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatHistoryResponse(BaseModel):
    """对话历史"""
    session_id: str
    messages: list[dict]


class ChatSendResponse(BaseModel):
    """非流式发送消息响应（降级使用）"""
    content: str
    session_id: str
    tool_calls_made: list[str] = []


# ============================================================
# SSE 事件类型
# ============================================================

# SSE 事件格式（通过 StreamingResponse 发送）:
#
# 1. event: tool_start
#    data: {"tool": "search_foods", "message": "正在搜索食物库..."}
#
# 2. event: tool_end
#    data: {"tool": "search_foods", "result_preview": "找到3个结果"}
#
# 3. event: token
#    data: {"content": "根据搜索结果显示..."}
#
# 4. event: done
#    data: {"session_id": "...", "tool_calls": ["search_foods"], "message_id": 123}
#
# 5. event: error
#    data: {"message": "发生错误"}

class SSEToolStart(BaseModel):
    tool: str
    message: str


class SSEToolEnd(BaseModel):
    tool: str
    result_preview: str


class SSEToken(BaseModel):
    content: str


class SSEDone(BaseModel):
    session_id: str
    tool_calls: list[str]
    message_id: int


class SSEError(BaseModel):
    message: str
