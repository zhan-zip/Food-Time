"""自定义食物模块 - API 路由（P2：DIY 烹饪建议 + 保存 + 我的菜谱）"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from src.database import get_db
from src.dependencies import get_current_user
from src.auth.models import User
from src.custom_food.models import CustomRecipe, CustomRecipeIngredient
from src.food.models import Food, FoodCategory
from src.services.deepseek import deepseek
from src.services.nutrition_ref import NUTRITION_REF

router = APIRouter(prefix="/api/custom", tags=["自定义食物"])


# ============================================================
# Schema
# ============================================================
class SuggestRequest(BaseModel):
    ingredients: list[str] = Field(default_factory=list, description="主料名称列表")
    seasonings: list[str] = Field(default_factory=list, description="调料名称列表")


class SaveRecipeRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="菜名")
    description: str | None = Field(None, max_length=500, description="简介")
    ingredients: list[str] = Field(..., min_length=1, description="食材名称列表")
    seasonings: list[str] = Field(default_factory=list, description="调料名称列表")
    cooking_method: str = Field(..., description="烹饪方式（wok/air_fryer/steamer）")
    cooking_steps: list[str] = Field(default_factory=list, description="烹饪步骤")
    estimated_calories: float | None = Field(None, description="预估热量（每100g）")
    publish_to_square: bool = Field(False, description="是否同时发布到广场")


# ============================================================
# POST /api/custom/suggest — AI 烹饪建议
# ============================================================
@router.post("/suggest")
async def suggest_recipe(
    body: SuggestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """根据已选食材给出烹饪建议：先数据库匹配 → 再 DeepSeek 回退"""
    if not body.ingredients:
        return {"source": "error", "matched": [], "error": "请至少选择一种主食材（肉类/海鲜/蔬菜/豆制品/蛋奶）"}
    all_items = set(body.ingredients + body.seasonings)

    # ---- ① 数据库匹配：foods 表按 name/tags 匹配 ----
    matched_recipes = []
    if all_items:
        # 对每个食材做模糊搜索，收集匹配的 food
        conditions = []
        for name in all_items:
            conditions.append(Food.name.like(f"%{name}%"))
        result = await db.execute(
            select(Food).where(or_(*conditions)).where(Food.is_public == True).limit(30)
        )
        candidates = result.scalars().all()

        # 计算每个候选菜谱与用户食材的交集大小
        for food in candidates:
            tags_str = ""
            if food.tags and isinstance(food.tags, dict):
                match_ingredients = food.tags.get("匹配食材", "")
                if match_ingredients:
                    tags_str = str(match_ingredients)
            search_text = food.name + tags_str
            intersection = sum(1 for item in all_items if item in search_text)
            if intersection >= 2:  # 至少匹配 2 种食材
                matched_recipes.append({
                    "id": food.id,
                    "name": food.name,
                    "cuisine": food.cuisine,
                    "calories_per_100g": float(food.calories_per_100g) if food.calories_per_100g else None,
                    "match_count": intersection,
                    "tags": food.tags,
                    "source": "database",
                })

        matched_recipes.sort(key=lambda x: x["match_count"], reverse=True)

    # 如果有匹配结果，直接返回
    if matched_recipes:
        return {
            "source": "database",
            "matched": matched_recipes[:5],  # 最多 5 个匹配
            "ai_suggestion": None,
        }

    # ---- ② DeepSeek 回退：生成烹饪建议 ----
    if not deepseek.is_configured:
        return {
            "source": "fallback",
            "matched": [],
            "ai_suggestion": {
                "name": f"创意料理（{', '.join(body.ingredients)}）",
                "cooking_method": "wok",
                "cooking_method_label": "炒锅",
                "steps": [
                    "1. 将所有食材洗净切好备用",
                    "2. 热锅凉油，先下主料翻炒至变色",
                    "3. 加入调料调味，翻炒均匀",
                    "4. 出锅装盘即可",
                ],
                "estimated_calories": 150,
                "estimated_time": "10分钟",
                "nutrition_note": "基于食材加权估算（中国食物成分表第六版）",
            },
        }

    prompt = (
        f"你是一位专业的中餐厨师。用户选择了以下食材和调料：\n"
        f"【主料】{', '.join(body.ingredients)}\n"
        f"【调料】{', '.join(body.seasonings) if body.seasonings else '无'}\n\n"
        "请给出一个最佳的烹饪建议，以 JSON 格式返回：\n"
        '{\n'
        '  "name": "菜名（10字以内）",\n'
        '  "cooking_method": "wok/air_fryer/steamer中选一个",\n'
        '  "cooking_method_label": "中文显示（炒锅/空气炸锅/蒸锅）",\n'
        '  "steps": ["步骤1", "步骤2", ...],\n'
        '  "estimated_calories": 数字（每100g千卡）,\n'
        '  "estimated_time": "预估烹饪时间（如15分钟）",\n'
        '  "nutrition_tip": "一句营养提示"\n'
        '}\n\n'
        "注意：只返回 JSON，不要包含其他文字。热量数据请基于常见菜品的合理范围估算。"
    )

    try:
        ai_resp = await deepseek.chat_simple([{"role": "user", "content": prompt}])
    except Exception as e:
        return {
            "source": "error",
            "matched": [],
            "error": f"AI 服务不可用: {e}",
        }

    if not ai_resp:
        return {
            "source": "error",
            "matched": [],
            "error": "AI 未返回有效建议",
        }

    # 解析 AI 返回的 JSON
    import json, re
    try:
        suggestion = json.loads(ai_resp)
    except json.JSONDecodeError:
        match = re.search(r'\{[\s\S]*\}', ai_resp)
        if match:
            try:
                suggestion = json.loads(match.group(0))
            except json.JSONDecodeError:
                return {"source": "error", "matched": [], "error": "AI 返回格式异常"}
        else:
            return {"source": "error", "matched": [], "error": "AI 返回格式异常"}

    return {
        "source": "ai",
        "matched": [],
        "ai_suggestion": {
            "name": suggestion.get("name", ""),
            "cooking_method": suggestion.get("cooking_method", "wok"),
            "cooking_method_label": suggestion.get("cooking_method_label", "炒锅"),
            "steps": suggestion.get("steps", []),
            "estimated_calories": suggestion.get("estimated_calories", 150),
            "estimated_time": suggestion.get("estimated_time", "15分钟"),
            "nutrition_tip": suggestion.get("nutrition_tip", ""),
        },
    }


# ============================================================
# POST /api/custom/save — 保存 DIY 食谱
# ============================================================
@router.post("/save")
async def save_recipe(
    body: SaveRecipeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """保存用户创建的 DIY 食谱"""
    # 查找或创建"自定义"分类
    cat_result = await db.execute(select(FoodCategory).where(FoodCategory.name == "自定义"))
    custom_cat = cat_result.scalar_one_or_none()
    if not custom_cat:
        custom_cat = FoodCategory(name="自定义", icon="", sort_order=99)
        db.add(custom_cat)
        await db.flush()

    # 估算营养数据（食材加权平均）
    est_calories = body.estimated_calories
    if not est_calories:
        total_cal = 0.0
        count = 0
        for name in body.ingredients:
            ref = NUTRITION_REF.get(name) or NUTRITION_REF.get(
                next((k for k in NUTRITION_REF if name in k or k in name), None)
            )
            if ref:
                total_cal += ref.get("calories", 0)
                count += 1
        est_calories = round(total_cal / count, 1) if count > 0 else None

    # 创建 Food 记录
    method_labels = {"wok": "炒锅", "air_fryer": "空气炸锅", "steamer": "蒸锅"}
    food = Food(
        name=body.name,
        category_id=custom_cat.id,
        cuisine=method_labels.get(body.cooking_method, "炒锅"),
        description=body.description,
        calories_per_100g=est_calories,
        tags={
            "来源": "DIY",
            "作者": current_user.nickname or current_user.email,
            "食材": body.ingredients,
            "调料": body.seasonings,
            "烹饪方式": method_labels.get(body.cooking_method, body.cooking_method),
            "营养数据来源": "中国食物成分表（第六版）- 基于食材加权估算",
        },
        source="custom",
        is_public=body.publish_to_square,
    )
    db.add(food)
    await db.flush()

    # 创建 CustomRecipe 记录
    recipe = CustomRecipe(
        user_id=current_user.id,
        food_id=food.id,
        cooking_steps=body.cooking_steps if body.cooking_steps else [],
        is_published=body.publish_to_square,
        publish_status="approved" if body.publish_to_square else "pending",
    )
    db.add(recipe)
    await db.flush()

    # 食材关联
    for name in body.ingredients:
        db.add(CustomRecipeIngredient(
            recipe_id=recipe.id,
            ingredient_name=name,
            ingredient_type="ingredient",
        ))
    for name in body.seasonings:
        db.add(CustomRecipeIngredient(
            recipe_id=recipe.id,
            ingredient_name=name,
            ingredient_type="seasoning",
        ))

    await db.commit()

    return {
        "success": True,
        "id": recipe.id,
        "food_id": food.id,
        "name": body.name,
        "published": body.publish_to_square,
        "message": "食谱保存成功" + ("，已发布到广场" if body.publish_to_square else ""),
    }


# ============================================================
# GET /api/custom/my — 我的自定义食谱列表
# ============================================================
@router.get("/my")
async def my_recipes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """我的自定义食谱列表"""
    result = await db.execute(
        select(CustomRecipe)
        .where(CustomRecipe.user_id == current_user.id)
        .order_by(CustomRecipe.created_at.desc())
        .limit(50)
    )
    recipes = result.scalars().all()

    items = []
    for r in recipes:
        food_result = await db.execute(select(Food).where(Food.id == r.food_id))
        food = food_result.scalar_one_or_none()
        items.append({
            "id": r.id,
            "food_id": r.food_id,
            "name": food.name if food else "未知菜谱",
            "calories_per_100g": float(food.calories_per_100g) if (food and food.calories_per_100g) else None,
            "cooking_method": food.cuisine if food else "",
            "steps": r.cooking_steps or [],
            "is_published": r.is_published,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        })

    return {"items": items, "total": len(items)}
