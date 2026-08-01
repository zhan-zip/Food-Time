"""饮食记录模块 - API 路由"""

from datetime import date, timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete

from src.database import get_db
from src.dependencies import get_current_user
from src.auth.models import User
from src.food.models import Food
from src.diet.models import DietRecord, UserPreference

router = APIRouter(prefix="/api/diet", tags=["饮食记录"])

# 营养方案B：烹饪方式热量修正系数（参考国内外烹饪营养学研究通用结论）
COOKING_FACTORS = {
    "stir-fry": 1.20,  # 炒
    "fry": 1.50,       # 炸
    "roast": 1.05, "bake": 1.05, "grill": 1.05,  # 烤
    "steam": 0.95,     # 蒸
    "boil": 0.90,      # 煮
    "braise": 1.10, "stew": 1.10,  # 炖
    "raw": 1.00, "mix": 1.00,      # 生/凉拌
}


def _cooking_factor(food) -> float:
    """根据食物 tags.cooking 返回热量修正系数（默认 1.00）"""
    import json
    tags = food.tags
    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except Exception:
            tags = {}
    if isinstance(tags, dict):
        cooking = tags.get("cooking")
        if cooking in COOKING_FACTORS:
            return COOKING_FACTORS[cooking]
    return 1.00


# ==================== Pydantic 模型 ====================

class DietRecordCreate(BaseModel):
    food_id: int = Field(..., gt=0, description="食物ID")
    meal_type: str = Field(..., pattern="^(breakfast|lunch|dinner|snack)$", description="餐别")
    quantity_g: float = Field(..., gt=0, le=10000, description="分量（克）")
    record_date: str | None = Field(default=None, description="日期 YYYY-MM-DD，默认今天")


# ==================== 查询饮食记录 ====================

@router.get("/records")
async def diet_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    meal_type: str | None = Query(None, pattern="^(breakfast|lunch|dinner|snack)$"),
    date_from: str | None = Query(None, description="开始日期 YYYY-MM-DD"),
    date_to: str | None = Query(None, description="结束日期 YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """查询当前用户的饮食记录（分页 + 筛选）"""
    conditions = [DietRecord.user_id == current_user.id]

    if meal_type:
        conditions.append(DietRecord.meal_type == meal_type)
    if date_from:
        conditions.append(DietRecord.record_date >= date.fromisoformat(date_from))
    if date_to:
        conditions.append(DietRecord.record_date <= date.fromisoformat(date_to))

    # 总数
    count_q = select(func.count(DietRecord.id)).where(and_(*conditions))
    total_result = await db.execute(count_q)
    total = total_result.scalar() or 0

    # 分页查询（关联 Food 获取名称和热量）
    q = (
        select(DietRecord, Food.name, Food.calories_per_100g)
        .join(Food, DietRecord.food_id == Food.id)
        .where(and_(*conditions))
        .order_by(DietRecord.record_date.desc(), DietRecord.record_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(q)
    rows = result.all()

    items = []
    for record, food_name, cal_per_100g in rows:
        cal = float(cal_per_100g) * float(record.quantity_g) / 100 if cal_per_100g else 0
        # 优先返回烹饪修正后的热量（方案B）
        display_cal = float(record.adjusted_calories) if record.adjusted_calories is not None else cal
        items.append({
            "id": record.id,
            "food_id": record.food_id,
            "food_name": food_name,
            "meal_type": record.meal_type,
            "quantity_g": float(record.quantity_g),
            "calories": round(display_cal, 1),
            "record_date": record.record_date.isoformat(),
            "record_time": record.record_time.strftime("%H:%M"),
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


# ==================== 新增饮食记录 ====================

@router.post("/records")
async def create_diet_record(
    body: DietRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """新增一条饮食记录"""
    # 校验 food 存在
    food_result = await db.execute(select(Food).where(Food.id == body.food_id))
    food = food_result.scalar_one_or_none()
    if not food:
        raise HTTPException(status_code=404, detail="食物不存在")

    rec_date = date.fromisoformat(body.record_date) if body.record_date else date.today()
    now = datetime.now()

    cal = float(food.calories_per_100g or 0) * body.quantity_g / 100
    factor = _cooking_factor(food)
    adjusted_cal = round(cal * factor, 2)

    record = DietRecord(
        user_id=current_user.id,
        food_id=body.food_id,
        meal_type=body.meal_type,
        quantity_g=body.quantity_g,
        record_date=rec_date,
        record_time=now.time(),
        adjusted_calories=adjusted_cal,
    )
    db.add(record)
    await db.flush()

    # 更新偏好统计
    await _update_preferences(db, current_user.id, food)

    await db.commit()

    return {
        "id": record.id,
        "food_name": food.name,
        "meal_type": record.meal_type,
        "quantity_g": body.quantity_g,
        "calories": round(cal, 1),
        "adjusted_calories": adjusted_cal,
        "record_date": rec_date.isoformat(),
        "message": "记录成功",
    }


# ==================== 删除饮食记录 ====================

@router.delete("/records/{record_id}")
async def delete_diet_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除一条饮食记录"""
    result = await db.execute(
        select(DietRecord).where(
            DietRecord.id == record_id,
            DietRecord.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    await db.delete(record)
    await db.commit()
    return {"message": "已删除"}


# ==================== 偏好分析 ====================

@router.get("/preferences")
async def preferences(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户的饮食偏好分析"""
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == current_user.id)
    )
    pref = result.scalar_one_or_none()

    if not pref:
        return {
            "spicy_level": 0,
            "sweet_level": 0,
            "hot_cold_ratio": 0.5,
            "fav_cuisines": [],
            "fav_tags": [],
            "total_records": 0,
        }

    return {
        "spicy_level": float(pref.spicy_level),
        "sweet_level": float(pref.sweet_level),
        "hot_cold_ratio": float(pref.hot_cold_ratio),
        "fav_cuisines": pref.fav_cuisines or [],
        "fav_tags": pref.fav_tags or [],
        "total_records": pref.total_records,
    }


# ==================== 营养分析 ====================

@router.get("/nutrition")
async def nutrition(
    days: int = Query(7, ge=1, le=90, description="统计天数"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户的营养摄入分析数据"""
    since = date.today() - timedelta(days=days - 1)

    q = (
        select(
            DietRecord.record_date,
            func.sum(func.coalesce(
                DietRecord.adjusted_calories,
                Food.calories_per_100g * DietRecord.quantity_g / 100,
            )).label("cal"),
            func.sum(Food.protein_per_100g * DietRecord.quantity_g / 100).label("pro"),
            func.sum(Food.fat_per_100g * DietRecord.quantity_g / 100).label("fat"),
            func.sum(Food.carbs_per_100g * DietRecord.quantity_g / 100).label("carbs"),
            func.sum(Food.fiber_per_100g * DietRecord.quantity_g / 100).label("fiber"),
        )
        .join(Food, DietRecord.food_id == Food.id)
        .where(
            DietRecord.user_id == current_user.id,
            DietRecord.record_date >= since,
        )
        .group_by(DietRecord.record_date)
        .order_by(DietRecord.record_date)
    )
    result = await db.execute(q)
    rows = result.all()

    daily = []
    total_cal = 0
    total_pro = 0
    total_fat = 0
    total_carbs = 0
    for row in rows:
        r_date, cal, pro, fat, carbs, fiber = row
        daily.append({
            "date": r_date.isoformat(),
            "calories": round(float(cal or 0), 1),
            "protein": round(float(pro or 0), 1),
            "fat": round(float(fat or 0), 1),
            "carbs": round(float(carbs or 0), 1),
            "fiber": round(float(fiber or 0), 1),
        })
        total_cal += float(cal or 0)
        total_pro += float(pro or 0)
        total_fat += float(fat or 0)
        total_carbs += float(carbs or 0)

    day_count = len(daily) or 1
    return {
        "days": daily,
        "avg_calories": round(total_cal / day_count, 1),
        "avg_protein": round(total_pro / day_count, 1),
        "avg_fat": round(total_fat / day_count, 1),
        "avg_carbs": round(total_carbs / day_count, 1),
        "total_days": len(daily),
    }


# ==================== 内部辅助函数 ====================

async def _update_preferences(db: AsyncSession, user_id: int, food: Food):
    """更新用户偏好统计（每次新增记录时调用）"""
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == user_id)
    )
    pref = result.scalar_one_or_none()

    if not pref:
        pref = UserPreference(
            user_id=user_id,
            total_records=0,
            fav_cuisines=[],
            fav_tags=[],
        )
        db.add(pref)

    pref.total_records = (pref.total_records or 0) + 1

    # 简易偏好更新：根据食物标签调整辣度/甜度
    import json
    tags = food.tags
    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except Exception:
            tags = {}
    if isinstance(tags, dict):
        spicy_map = {"high": 1.0, "medium": 0.5, "low": 0.2, "none": 0}
        if "spicy" in tags:
            new_spicy = spicy_map.get(tags["spicy"], 0)
            current = float(pref.spicy_level or 0)
            n = pref.total_records
            pref.spicy_level = current * (n - 1) / n + new_spicy / n

    # 更新偏好菜系
    if food.cuisine:
        fav_cuisines = list(pref.fav_cuisines or [])
        fav_cuisines.append(food.cuisine)
        # 保持最近10个（可扩展为计数）
        pref.fav_cuisines = fav_cuisines[-10:]
