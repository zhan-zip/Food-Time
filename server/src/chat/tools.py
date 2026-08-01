"""工具定义与执行 — 对应 qq-agent 的 llm/tools.py

10 个工具，按 OpenAI function calling 格式定义。
扩展新工具只需三步：
  1. 在 TOOLS 列表追加定义
  2. 在 execute_tool() 添加分支
  3. 在 TOOLS_README 添加描述
"""

import json
from typing import Any

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.food.models import Food, FoodCategory
from src.diet.models import DietRecord, UserPreference
from src.expense.models import ExpenseRecord
from src.chat.models import LongMemory

# ============================================================
# TOOLS — OpenAI function calling 格式
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_foods",
            "description": "搜索食物库。根据关键词和分类查找食物及其营养数据。当用户询问某种食物、搜索菜品、或需要查找营养信息时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "搜索关键词（食物名称）"},
                    "category_id": {"type": "integer", "description": "分类ID（可选）"},
                },
                "required": ["keyword"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_food_nutrition",
            "description": "获取某道食物的详细营养数据（热量/蛋白质/脂肪/碳水/纤维/钠含量）。当用户询问某具体食物的营养成分时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "food_name": {"type": "string", "description": "食物名称"},
                },
                "required": ["food_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_preferences",
            "description": "获取当前用户的饮食偏好分析结果，包括辣度、甜度、偏好菜系、偏好标签等。用于个性化推荐时调用。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_diet_records",
            "description": "获取当前用户最近N天的饮食记录列表。当用户询问'我最近吃了什么'或需要分析营养摄入时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "查询最近几天，默认7天"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_expense_summary",
            "description": "获取当前用户账单消费统计汇总。当用户询问花了多少钱、消费情况时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "period": {"type": "string", "description": "统计周期：week/本月，month/本月"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_recipe",
            "description": "根据用户偏好和营养需求推荐食谱。综合用户的饮食偏好、近期饮食记录和营养数据给出个性化推荐。",
            "parameters": {
                "type": "object",
                "properties": {
                    "preference": {"type": "string", "description": "偏好描述：如低脂/高蛋白/清淡/辣的/素菜"},
                    "calories_max": {"type": "integer", "description": "每份最大热量限制（kcal）"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recommend_food",
            "description": "综合推荐食物。当用户不知道吃什么、需要决策辅助时调用。综合偏好、营养和季节因素推荐。",
            "parameters": {
                "type": "object",
                "properties": {
                    "meal_type": {"type": "string", "description": "餐别：breakfast/午餐、lunch/午餐、dinner/晚餐、snack/零食"},
                    "scenario": {"type": "string", "description": "场景：quick/快速、healthy/健康、indulge/放纵"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_diet_record",
            "description": "为用户记录今天吃了什么。当用户说'我吃了XXX'、'帮我记一下XXX'时调用此工具。必须先与用户确认食物名称和分量。",
            "parameters": {
                "type": "object",
                "properties": {
                    "food_name": {"type": "string", "description": "食物名称"},
                    "meal_type": {"type": "string", "description": "餐别：breakfast/早餐、lunch/午餐、dinner/晚餐、snack/零食"},
                    "quantity_g": {"type": "number", "description": "分量（克）"},
                },
                "required": ["food_name", "meal_type", "quantity_g"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_food_image",
            "description": "分析用户上传的食物图片，识别图片中的食物种类并估算营养数据。当用户上传食物照片时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_url": {"type": "string", "description": "图片URL或base64数据"},
                },
                "required": ["image_url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_nearby_food",
            "description": "获取用户附近可推荐的食物/餐厅信息（基于地理位置）。选做功能。",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "城市名或区域"},
                    "cuisine": {"type": "string", "description": "菜系偏好（可选）"},
                },
                "required": ["location"],
            },
        },
    },
]

# ============================================================
# TOOLS_README — 嵌入 system prompt 的工具可读说明
# ============================================================

TOOLS_README = """【可用工具清单】

1. search_foods(keyword, category_id?) — 搜索食物库，返回匹配的食物和营养数据
2. get_food_nutrition(food_name) — 获取指定食物的详细营养数据
3. get_user_preferences() — 获取用户饮食偏好分析（辣度/甜度/偏好菜系）
4. get_diet_records(days?) — 获取用户最近N天饮食记录
5. get_expense_summary(period?) — 获取用户账单统计
6. suggest_recipe(preference?, calories_max?) — 综合推荐食谱
7. recommend_food(meal_type?, scenario?) — 食物决策辅助
8. add_diet_record(food_name, meal_type, quantity_g) — 记录用户饮食
9. analyze_food_image(image_url) — 分析食物图片
10. get_nearby_food(location, cuisine?) — 附近食物推荐（选做）

【工具调用规则】
- 涉及食物营养数据 → 必须调用 search_foods 或 get_food_nutrition
- 涉及个性化推荐 → 先调用 get_user_preferences 再推荐
- 涉及营养分析 → 先调用 get_diet_records 再分析
- 用户说"我吃了/帮我记" → 调用 add_diet_record
- 所有建议必须有工具返回的真实数据支撑，严禁编造"""


# ============================================================
# execute_tool — 统一执行入口
# ============================================================

async def execute_tool(
    db: AsyncSession,
    user_id: int,
    tool_name: str,
    arguments: dict[str, Any],
) -> str:
    """执行工具并返回文本结果"""

    try:
        # ---- 工具 1：搜索食物 ----
        if tool_name == "search_foods":
            keyword = arguments.get("keyword", "")
            if not keyword:
                return "[错误] 搜索关键词不能为空"

            q = select(Food).where(Food.is_public == True)
            q = q.where(Food.name.contains(keyword))
            q = q.limit(10)

            result = await db.execute(q)
            foods = result.scalars().all()

            if not foods:
                return f"未找到与'{keyword}'相关的食物"

            lines = [f"搜索'{keyword}'共找到 {len(foods)} 个结果："]
            for f in foods:
                cal = float(f.calories_per_100g) if f.calories_per_100g else 0
                protein = float(f.protein_per_100g) if f.protein_per_100g else 0
                lines.append(
                    f"- ID:{f.id} {f.name}｜{f.cuisine or '通用'}｜{cal:.0f}kcal/100g｜蛋白质{protein:.1f}g"
                )
            return "\n".join(lines)

        # ---- 工具 2：获取营养详情 ----
        elif tool_name == "get_food_nutrition":
            food_name = arguments.get("food_name", "")
            if not food_name:
                return "[错误] 请提供食物名称"

            q = select(Food).where(
                Food.name.contains(food_name),
                Food.is_public == True,
            ).limit(1)
            result = await db.execute(q)
            food = result.scalar_one_or_none()

            if not food:
                return f"未找到'{food_name}'的营养数据"

            return (
                f"【{food.name}】营养数据 (每100克)\n"
                f"热量：{food.calories_per_100g or '未知'} kcal\n"
                f"蛋白质：{food.protein_per_100g or '未知'} g\n"
                f"脂肪：{food.fat_per_100g or '未知'} g\n"
                f"碳水：{food.carbs_per_100g or '未知'} g\n"
                f"膳食纤维：{food.fiber_per_100g or '未知'} g\n"
                f"钠：{food.sodium_per_100g or '未知'} mg\n"
                f"菜系：{food.cuisine or '通用'}\n"
                f"标签：{food.tags or '无'}"
            )

        # ---- 工具 3：获取用户偏好 ----
        elif tool_name == "get_user_preferences":
            result = await db.execute(
                select(UserPreference).where(UserPreference.user_id == user_id)
            )
            pref = result.scalar_one_or_none()

            if not pref:
                # 获取长期记忆作为偏好参考
                lm_result = await db.execute(
                    select(LongMemory).where(LongMemory.user_id == user_id)
                )
                memories = lm_result.scalars().all()
                if memories:
                    facts = "\n".join(f"- {m.fact}" for m in memories)
                    return f"该用户暂无结构化偏好分析。但从长期记忆中提取了以下信息：\n{facts}\n\n建议：引导用户多使用饮食记录功能以生成更精准的偏好分析。"
                return "该用户暂无偏好数据。建议引导用户多使用饮食记录功能。"

            fav_cuisines = pref.fav_cuisines or []
            fav_tags = pref.fav_tags or []
            if isinstance(fav_cuisines, str):
                fav_cuisines = json.loads(fav_cuisines)
            if isinstance(fav_tags, str):
                fav_tags = json.loads(fav_tags)

            return (
                f"【用户饮食偏好】\n"
                f"辣度等级：{float(pref.spicy_level):.1f}/1.0\n"
                f"甜度等级：{float(pref.sweet_level):.1f}/1.0\n"
                f"冷热偏好：{float(pref.hot_cold_ratio):.1f}（0=偏爱冷食，1=偏爱热食）\n"
                f"偏好菜系：{', '.join(fav_cuisines) if fav_cuisines else '暂无'}\n"
                f"偏好标签：{', '.join(fav_tags) if fav_tags else '暂无'}\n"
                f"总记录数：{pref.total_records}"
            )

        # ---- 工具 4：获取饮食记录 ----
        elif tool_name == "get_diet_records":
            days = arguments.get("days", 7)

            from datetime import date, timedelta
            since = date.today() - timedelta(days=days)

            q = (
                select(DietRecord, Food.name, Food.calories_per_100g)
                .join(Food, DietRecord.food_id == Food.id)
                .where(
                    DietRecord.user_id == user_id,
                    DietRecord.record_date >= since,
                )
                .order_by(DietRecord.record_date.desc(), DietRecord.record_time.desc())
                .limit(30)
            )
            result = await db.execute(q)
            records = result.all()

            if not records:
                return f"最近 {days} 天暂无饮食记录。建议使用 'add_diet_record' 工具帮用户记录饮食。"

            total_kcal = 0
            lines = [f"最近 {days} 天饮食记录（共 {len(records)} 条）："]
            for r, food_name, cal_per_100g in records:
                cal = float(cal_per_100g) * float(r.quantity_g) / 100 if cal_per_100g else 0
                total_kcal += cal
                lines.append(
                    f"- {r.record_date} {r.meal_type}：{food_name} {float(r.quantity_g):.0f}g（约{cal:.0f}kcal）"
                )
            lines.append(f"\n总热量估算：约 {total_kcal:.0f} kcal")
            return "\n".join(lines)

        # ---- 工具 5：获取账单统计 ----
        elif tool_name == "get_expense_summary":
            period = arguments.get("period", "month")

            from datetime import date, timedelta
            if period == "week":
                since = date.today() - timedelta(days=7)
            else:
                since = date.today().replace(day=1)

            # 按分类统计
            q = (
                select(
                    ExpenseRecord.category,
                    func.sum(ExpenseRecord.amount).label("total"),
                    func.count().label("count"),
                )
                .where(
                    ExpenseRecord.user_id == user_id,
                    ExpenseRecord.record_date >= since,
                )
                .group_by(ExpenseRecord.category)
            )
            result = await db.execute(q)
            stats = result.all()

            if not stats:
                return f"该周期内暂无消费记录"

            lines = ["【账单统计】"]
            grand_total = 0
            for cat, total, count in stats:
                lines.append(f"- {cat}：{float(total):.2f} 元（{count}笔）")
                grand_total += float(total)
            lines.append(f"\n合计：{grand_total:.2f} 元")
            return "\n".join(lines)

        # ---- 工具 6：推荐食谱 ----
        elif tool_name == "suggest_recipe":
            preference = arguments.get("preference", "")
            calories_max = arguments.get("calories_max")

            # 基础查询
            q = select(Food).where(Food.is_public == True).limit(10)
            if calories_max:
                q = q.where(Food.calories_per_100g <= calories_max)

            result = await db.execute(q)
            foods = result.scalars().all()

            if not foods:
                return "暂无符合条件的食谱数据"

            lines = [f"推荐食谱（偏好：{preference or '综合'}）："]
            for f in foods[:5]:
                cal = float(f.calories_per_100g) if f.calories_per_100g else 0
                lines.append(
                    f"- {f.name}｜{f.cuisine or '通用'}｜{cal:.0f}kcal/100g"
                )

            # 附上偏好信息用于后续推荐
            if preference:
                lines.append(f"\n说明：以上为基于偏好'{preference}'的推荐，供参考")
            return "\n".join(lines)

        # ---- 工具 7：综合推荐 ----
        elif tool_name == "recommend_food":
            meal_type = arguments.get("meal_type", "")
            scenario = arguments.get("scenario", "")

            q = select(Food).where(Food.is_public == True).order_by(func.rand()).limit(5)
            result = await db.execute(q)
            foods = result.scalars().all()

            if not foods:
                return "暂无食物数据"

            meal_map = {"breakfast": "早餐", "lunch": "午餐", "dinner": "晚餐", "snack": "零食"}
            scenario_map = {"quick": "快速省时", "healthy": "健康轻食", "indulge": "犒劳自己"}

            lines = []
            lines.append(
                f"为您推荐（{meal_map.get(meal_type, meal_type or '任意餐别')}｜{scenario_map.get(scenario, scenario or '综合')}）："
            )
            for f in foods:
                cal = float(f.calories_per_100g) if f.calories_per_100g else 0
                lines.append(f"- {f.name}｜{cal:.0f}kcal/100g")

            lines.append("\n提示：如需更精准推荐，可使用我的建议记录日常饮食以积累偏好数据。")
            return "\n".join(lines)

        # ---- 工具 8：记录饮食 ----
        elif tool_name == "add_diet_record":
            food_name = arguments.get("food_name", "")
            meal_type = arguments.get("meal_type", "lunch")
            quantity_g = arguments.get("quantity_g", 150)

            if not food_name:
                return "[错误] 请提供食物名称"

            # 查找食物
            q = select(Food).where(Food.name.contains(food_name)).limit(1)
            result = await db.execute(q)
            food = result.scalar_one_or_none()

            if not food:
                return (
                    f"未找到'{food_name}'，无法记录。"
                    f"建议先使用 search_foods 搜索确认正确的食物名称。"
                )

            from datetime import date, datetime
            record = DietRecord(
                user_id=user_id,
                food_id=food.id,
                meal_type=meal_type,
                quantity_g=quantity_g,
                record_date=date.today(),
                record_time=datetime.now().time(),
            )
            db.add(record)
            await db.commit()

            cal = float(food.calories_per_100g) * quantity_g / 100 if food.calories_per_100g else 0
            return (
                f"已记录：{food.name} {quantity_g:.0f}g｜{meal_type}\n"
                f"约 {cal:.0f} kcal｜数据库ID: {record.id}"
            )

        # ---- 工具 9：分析食物图片 ----
        elif tool_name == "analyze_food_image":
            image_url = arguments.get("image_url", "")
            if not image_url:
                return "[错误] 请提供图片URL或base64数据"

            from src.services.qwen import qwen_vl, is_safe_image_url
            if not await is_safe_image_url(image_url):
                return "[错误] 图片 URL 不合法：仅支持 https:// 公网图片链接或 base64 数据"
            if not qwen_vl.is_configured:
                return (
                    "Qwen VL 视觉模型未配置（请在 .env 中填写 QWEN_API_KEY）。\n"
                    "建议：请用户以文字描述食物内容，你可通过 search_foods 查找营养数据。"
                )

            result = await qwen_vl.analyze_food(image_url)
            if result:
                return f"【图片分析结果】\n{result}\n\n接下来你可以用 search_foods 核对营养数据。"
            return "图片分析失败，请尝试用文字描述食物内容。"

        # ---- 工具 10：附近推荐（占位） ----
        elif tool_name == "get_nearby_food":
            location = arguments.get("location", "")
            if not location:
                return "[错误] 请提供城市或区域名称"
            return (
                f"[占位] {location} 附近暂无餐厅数据。\n"
                "该功能需要接入地图API，为选做功能。可建议用户使用 search_foods 查找当地特色菜。"
            )

        else:
            return f"[错误] 未知工具：{tool_name}"

    except Exception as e:
        return f"[工具执行错误] {tool_name}: {e}"
