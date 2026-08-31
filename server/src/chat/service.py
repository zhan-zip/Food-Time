"""AI 对话核心管线 — 对应 qq-agent 的 core/message_processor.py

负责：
1. 构建 5 层 System Prompt
2. 短期记忆管理（最近 20 条上下文）
3. 长期记忆提取（每 6 轮用户消息）
4. RAG 增强（食物库自动语义搜索）
5. 多轮 Tool-Calling 循环（最多 3 轮）
6. SSE 流式输出 + 工具进度事件

使用方式：
    service = ChatService(db, user_id, session_id)
    async for event in service.run(message):
        yield event
"""

import json
import os
from datetime import datetime
from typing import AsyncGenerator, Any

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.chat.models import Conversation, LongMemory
from src.chat.tools import TOOLS, TOOLS_README, execute_tool
from src.services.deepseek import deepseek
from src.services.vector_store import vector_store

# 长期记忆提取周期
MEMORY_EXTRACT_INTERVAL = 6
MEMORY_EXTRACT_HISTORY = 12

# 工具调用最大轮数
MAX_TOOL_ROUNDS = 3

# 上下文窗口
MAX_HISTORY_MESSAGES = 20

# persona.txt 路径
_PERSONA_PATH = os.path.join(os.path.dirname(__file__), "persona.txt")


def _read_persona() -> str:
    """读取 persona.txt，失败时返回默认人设"""
    try:
        with open(_PERSONA_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "你是食光记平台的AI营养助手。"


# 模块级缓存：只读取一次 persona.txt，避免每次请求重复 open()
_PERSONA_CONTENT = _read_persona()


class ChatService:
    """AI 对话管线"""

    def __init__(self, db: AsyncSession, user_id: int, session_id: str):
        self.db = db
        self.user_id = user_id
        self.session_id = session_id

    # ===========================================================
    # 主入口
    # ===========================================================
    async def run(self, user_message: str, image_url: str | None = None) -> AsyncGenerator[dict, None]:
        """运行对话管线，yield SSE 事件"""

        # 0. 判断是否有 API Key
        if not deepseek.is_configured:
            yield _event("token", {"content": "AI 功能尚未配置。请在服务端 .env 文件中填写 DEEPSEEK_API_KEY。"})
            yield _event("done", {"session_id": self.session_id, "tool_calls": [], "message_id": 0})
            return

        # 1. 构建 system prompt
        system_prompt = await self._build_system_prompt(user_message)

        # 2. 获取历史消息
        history = await self._get_history()
        messages = [dict(role=h["role"], content=h["content"]) for h in history]
        messages.append(dict(role="user", content=user_message))

        # 3. 构建完整 messages（system + history + user）
        full_messages = [dict(role="system", content=system_prompt)] + messages

        # 4. 多轮 tool-calling 循环
        tool_calls_made = []
        for _round in range(MAX_TOOL_ROUNDS):
            response = await deepseek.chat_with_tools(full_messages, TOOLS)

            if response is None:
                # API 故障 → 降级为无工具调用
                break

            tool_calls = getattr(response, "tool_calls", None)
            if not tool_calls:
                # 没有工具调用 → LLM 直接回答
                break

            # 追加 assistant 消息（含 tool_calls）
            full_messages.append(_serialize_message(response))

            # 执行每个 tool
            for tc in tool_calls:
                fn = tc.function
                tool_name = fn.name
                args = json.loads(fn.arguments) if fn.arguments else {}

                # 发送工具开始事件
                yield _event("tool_start", {
                    "tool": tool_name,
                    "message": self._tool_message(tool_name, args),
                })

                # 执行工具
                tool_result = await execute_tool(self.db, self.user_id, tool_name, args)
                tool_calls_made.append(tool_name)

                # 发送工具结束事件
                preview = tool_result[:120] + ("..." if len(tool_result) > 120 else "")
                yield _event("tool_end", {"tool": tool_name, "result_preview": preview})

                # 追加 tool 结果
                full_messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": tool_result,
                })

        # 5. 流式输出最终回答
        response_text = ""
        async for token in deepseek.chat_stream(full_messages):
            if token:
                response_text += token
                yield _event("token", {"content": token})

        # 6. 保存到数据库
        await self._save_message("user", user_message)
        if response_text:
            await self._save_message("assistant", response_text)

        # 7. 长期记忆提取
        await self._maybe_extract_memory()

        # 8. 完成
        yield _event("done", {
            "session_id": self.session_id,
            "tool_calls": tool_calls_made,
            "message_id": 0,
        })

    # ===========================================================
    # 5 层 System Prompt 构建
    # ===========================================================
    async def _build_system_prompt(self, user_message: str) -> str:
        """构建分层 System Prompt"""

        now_str = datetime.now().strftime("%Y年%m月%d日 %H:%M")

        # Layer 1: 最高优先级规则
        layer1 = f"""【最高优先级规则】
- 当前时间：{now_str}
- 严禁编造任何食物的营养数据（热量、蛋白质、脂肪、碳水等）。所有营养数据必须来自工具调用结果。
- 当用户询问食物营养信息时，务必先调用 search_foods 或 get_food_nutrition 工具获取真实数据，再回答。
- 当用户说"我吃了XX"、"帮我记一下"时，务必调用 add_diet_record 工具记录。
- 不提供医疗诊断建议。涉及疾病/过敏/处方问题时，建议用户咨询专业医生。
- 自然融入：把工具/数据库返回的数据用自然、口语化的方式融入回答（如"我看你最近…""根据你记录的…""这道菜热量约…，很适合你"），像和朋友聊天一样引用数据；不要机械罗列"根据数据1…数据2…"，让建议读起来自然连贯、有温度。"""

        # Layer 2: 人设（热加载）
        layer2 = self._load_persona()

        # Layer 3: 长期记忆 + 用户信息
        layer3 = f"【当前用户】\n用户ID: {self.user_id}\n"
        long_mem = await self._get_long_memories()
        if long_mem:
            layer3 += f"\n【长期记忆】\n关于这位用户你已知：\n{long_mem}"

        # Layer 4: RAG 增强（自动语义搜索）
        layer4 = ""
        if vector_store.is_ready:
            rag_hits = await vector_store.search(user_message, deepseek.embed, n_results=3)
            if rag_hits:
                hit_texts = []
                for h in rag_hits:
                    doc = h.get("document", "")
                    if doc:
                        hit_texts.append(f"- {doc}")
                if hit_texts:
                    layer4 = f"\n【预获取信息 — 食物库语义搜索】\n以下是数据库中与用户问题相关的食物，可作为推荐参考：\n" + "\n".join(hit_texts)

        # Layer 5: 工具清单 + 规则
        layer5 = f"\n{TOOLS_README}"

        return f"{layer1}\n---\n{layer2}\n---\n{layer3}{layer4}\n---\n{layer5}"

    def _load_persona(self) -> str:
        """返回模块级缓存的 persona 内容（启动时读取一次）"""
        return _PERSONA_CONTENT

    # ===========================================================
    # 历史消息管理
    # ===========================================================
    async def _get_history(self) -> list[dict]:
        """获取最近 N 条消息"""
        q = (
            select(Conversation)
            .where(
                Conversation.user_id == self.user_id,
                Conversation.session_id == self.session_id,
            )
            .order_by(desc(Conversation.created_at))
            .limit(MAX_HISTORY_MESSAGES)
        )
        result = await self.db.execute(q)
        msgs = result.scalars().all()
        # 翻转回时间顺序
        msgs = list(reversed(msgs))
        return [{"role": m.role, "content": m.content} for m in msgs]

    async def _save_message(self, role: str, content: str, tool_name: str | None = None):
        """保存消息到数据库"""
        msg = Conversation(
            user_id=self.user_id,
            session_id=self.session_id,
            role=role,
            content=content,
            tool_name=tool_name,
        )
        self.db.add(msg)
        await self.db.commit()

    # ===========================================================
    # 长期记忆管理
    # ===========================================================
    async def _get_long_memories(self) -> str:
        """获取用户长期记忆"""
        q = (
            select(LongMemory)
            .where(LongMemory.user_id == self.user_id)
            .order_by(LongMemory.importance.desc())
            .limit(10)
        )
        result = await self.db.execute(q)
        memories = result.scalars().all()
        if not memories:
            return ""
        return "\n".join(f"- {m.fact}" for m in memories)

    async def _maybe_extract_memory(self):
        """每 N 轮提取一次长期记忆"""
        # 统计用户消息数
        q = select(func.count()).select_from(Conversation).where(
            Conversation.user_id == self.user_id,
            Conversation.session_id == self.session_id,
            Conversation.role == "user",
        )
        result = await self.db.execute(q)
        count = result.scalar() or 0

        if count > 0 and count % MEMORY_EXTRACT_INTERVAL == 0:
            await self._extract_memory()

    async def _extract_memory(self):
        """从最近对话中提取长期记忆"""
        q = (
            select(Conversation)
            .where(
                Conversation.user_id == self.user_id,
                Conversation.session_id == self.session_id,
            )
            .order_by(desc(Conversation.created_at))
            .limit(MEMORY_EXTRACT_HISTORY)
        )
        result = await self.db.execute(q)
        msgs = result.scalars().all()
        msgs = list(reversed(msgs))

        if not msgs:
            return

        transcript = "\n".join(f"[{m.role}] {m.content[:200]}" for m in msgs)

        extract_prompt = f"""从以下对话中提取值得长期记忆的用户事实。只提取与饮食偏好、口味、饮食习惯、过敏原、忌口、健康目标相关的事实。不提取无关的闲聊内容。

输出JSON格式：{{"facts": ["事实1", "事实2"]}} 如果没有值得记忆的事实，输出 {{"facts": []}}

对话内容：
{transcript}"""

        resp = await deepseek.chat_simple([
            {"role": "system", "content": "你是一个信息提取助手。仅输出JSON，不要其他内容。"},
            {"role": "user", "content": extract_prompt},
        ])

        if not resp:
            return

        try:
            data = json.loads(resp.strip().removeprefix("```json").removesuffix("```").strip())
            new_facts = data.get("facts", [])
        except (json.JSONDecodeError, AttributeError):
            return

        if not new_facts:
            return

        # 去重 + 保存
        existing_q = select(LongMemory).where(LongMemory.user_id == self.user_id)
        existing_result = await self.db.execute(existing_q)
        existing_facts = {m.fact for m in existing_result.scalars().all()}

        for fact in new_facts:
            if fact not in existing_facts:
                mem = LongMemory(
                    user_id=self.user_id,
                    fact=fact,
                    importance=1,
                    source_session=self.session_id,
                )
                self.db.add(mem)
                existing_facts.add(fact)

        await self.db.commit()

    # ===========================================================
    # 工具
    # ===========================================================
    @staticmethod
    def _tool_message(tool_name: str, args: dict) -> str:
        """工具调用的用户友好提示"""
        messages = {
            "search_foods": f"正在搜索食物库：{args.get('keyword', '')}...",
            "get_food_nutrition": f"正在查询 {args.get('food_name', '')} 的营养数据...",
            "get_user_preferences": "正在读取您的饮食偏好...",
            "get_diet_records": "正在查看您的饮食记录...",
            "get_expense_summary": "正在统计您的消费记录...",
            "suggest_recipe": "正在为您推荐食谱...",
            "recommend_food": "正在为您挑选食物...",
            "add_diet_record": f"正在记录：{args.get('food_name', '')}...",
            "analyze_food_image": "正在分析食物图片...",
            "get_nearby_food": f"正在搜索 {args.get('location', '')} 附近的美食...",
            "get_daily_nutrition_assessment": "正在评估您的营养摄入（对照膳食指南）...",
            "get_web_search": f"正在联网搜索：{args.get('query', '')}...",
        }
        return messages.get(tool_name, f"正在调用 {tool_name}...")


# ============================================================
# SSE 事件辅助
# ============================================================
def _event(event_type: str, data: dict) -> dict:
    return {"type": event_type, "data": data}


def _serialize_message(message: Any) -> dict:
    """将 OpenAI message 序列化为 dict"""
    d = {"role": message.role, "content": message.content or ""}
    if hasattr(message, "tool_calls") and message.tool_calls:
        d["tool_calls"] = [
            {
                "id": tc.id,
                "type": tc.type,
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in message.tool_calls
        ]
    return d
