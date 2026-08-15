"""Food-Time MCP Server: 把饮食能力暴露给外部 agent (如 qq-agent bot) 调用。

独立模块, 不改动现有代码。复用 src.chat.tools.execute_tool + src.database.async_session。
运行: 在 server/ 目录  python -m src.mcp_integration.server   (stdio)
"""
import asyncio
import logging
from typing import Optional

from mcp.server import MCPServer

from src.database import async_session
from src.chat.tools import execute_tool

logger = logging.getLogger("food_time_mcp")

# 暴露的 6 个核心饮食工具
EXPOSE = [
    "search_foods", "get_food_nutrition", "get_diet_records",
    "get_expense_summary", "suggest_recipe", "get_daily_nutrition_assessment",
]


def create_food_mcp() -> MCPServer:
    """创建 Food-Time MCP Server (只创建, 不启动)"""
    server = MCPServer(
        name="food-time",
        version="0.1",
        description="饮食助手能力接口: 搜索食物/查营养/饮食记录/账单统计/推荐食谱/营养评估",
        instructions=(
            "这是 Food-Time 饮食助手的能力接口。提供食物搜索、营养查询、饮食记录、"
            "账单统计、食谱推荐、营养评估能力。部分工具需要 food_user_id 指定用户。"
        ),
    )

    async def _run(user_id: int, tool_name: str, args: dict) -> str:
        async with async_session() as db:
            return await execute_tool(db, user_id, tool_name, args)

    @server.tool()
    async def search_foods(keyword: str, food_user_id: int = 0,
                           category_id: Optional[int] = None) -> str:
        """搜索食物库, 返回匹配的食物及其营养数据。"""
        args: dict = {"keyword": keyword}
        if category_id is not None:
            args["category_id"] = category_id
        return await _run(food_user_id, "search_foods", args)

    @server.tool()
    async def get_food_nutrition(food_name: str, food_user_id: int = 0) -> str:
        """获取某道食物的详细营养数据(热量/蛋白质/脂肪/碳水/纤维/钠)。"""
        return await _run(food_user_id, "get_food_nutrition", {"food_name": food_name})

    @server.tool()
    async def get_diet_records(food_user_id: int, days: int = 7) -> str:
        """获取指定用户最近 N 天的饮食记录。"""
        return await _run(food_user_id, "get_diet_records", {"days": days})

    @server.tool()
    async def get_expense_summary(food_user_id: int,
                                  period: Optional[str] = None) -> str:
        """获取指定用户的账单消费统计(period: week/month)。"""
        args: dict = {}
        if period:
            args["period"] = period
        return await _run(food_user_id, "get_expense_summary", args)

    @server.tool()
    async def suggest_recipe(food_user_id: int,
                             preference: Optional[str] = None,
                             calories_max: Optional[int] = None) -> str:
        """根据用户偏好和营养需求推荐食谱。"""
        args: dict = {}
        if preference:
            args["preference"] = preference
        if calories_max is not None:
            args["calories_max"] = calories_max
        return await _run(food_user_id, "suggest_recipe", args)

    @server.tool()
    async def get_daily_nutrition_assessment(food_user_id: int,
                                             days: int = 7) -> str:
        """评估用户近 N 天饮食摄入, 对照《中国居民膳食指南》给出达标/偏高/偏低结论。"""
        return await _run(food_user_id, "get_daily_nutrition_assessment", {"days": days})

    return server


if __name__ == "__main__":
    async def _main():
        await create_food_mcp().run_stdio_async()

    asyncio.run(_main())
