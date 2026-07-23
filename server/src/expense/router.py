"""记账模块 - API 路由"""

from datetime import date, timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

import base64
import tempfile
import os

from src.database import get_db
from src.dependencies import get_current_user
from src.auth.models import User
from src.expense.models import ExpenseRecord
from src.services.qwen import qwen_vl

router = APIRouter(prefix="/api/expense", tags=["记账"])


# ==================== Pydantic 模型 ====================

class ExpenseRecordCreate(BaseModel):
    amount: float = Field(..., gt=0, le=999999.99, description="金额")
    category: str = Field(..., description="分类: food(餐饮)/delivery(外卖)/snack(零食)/drink(饮品)/grocery(食材采购)")
    description: str | None = Field(default=None, max_length=500, description="备注")
    record_date: str | None = Field(default=None, description="日期 YYYY-MM-DD，默认今天")


# ==================== 查询账单 ====================

@router.get("/records")
async def expense_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """查询当前用户的账单记录（分页 + 筛选）"""
    conditions = [ExpenseRecord.user_id == current_user.id]

    if category:
        conditions.append(ExpenseRecord.category == category)
    if date_from:
        conditions.append(ExpenseRecord.record_date >= date.fromisoformat(date_from))
    if date_to:
        conditions.append(ExpenseRecord.record_date <= date.fromisoformat(date_to))

    # 总数
    count_q = select(func.count(ExpenseRecord.id)).where(and_(*conditions))
    total_result = await db.execute(count_q)
    total = total_result.scalar() or 0

    # 总金额
    sum_q = select(func.sum(ExpenseRecord.amount)).where(and_(*conditions))
    sum_result = await db.execute(sum_q)
    total_amount = float(sum_result.scalar() or 0)

    # 分页
    q = (
        select(ExpenseRecord)
        .where(and_(*conditions))
        .order_by(ExpenseRecord.record_date.desc(), ExpenseRecord.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(q)
    records = result.scalars().all()

    items = []
    for r in records:
        items.append({
            "id": r.id,
            "amount": float(r.amount),
            "category": r.category,
            "description": r.description or "",
            "record_date": r.record_date.isoformat(),
            "input_method": r.input_method,
        })

    return {
        "items": items,
        "total": total,
        "total_amount": round(total_amount, 2),
        "page": page,
        "page_size": page_size,
    }


# ==================== 新增账单 ====================

CATEGORY_NAMES = {
    "food": "餐饮", "delivery": "外卖", "snack": "零食",
    "drink": "饮品", "grocery": "食材采购",
}

@router.post("/records")
async def create_expense_record(
    body: ExpenseRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """新增一条账单记录"""
    if body.category not in CATEGORY_NAMES:
        raise HTTPException(status_code=400, detail=f"无效分类，可选: {list(CATEGORY_NAMES.keys())}")

    rec_date = date.fromisoformat(body.record_date) if body.record_date else date.today()

    record = ExpenseRecord(
        user_id=current_user.id,
        amount=body.amount,
        category=body.category,
        description=body.description,
        record_date=rec_date,
        input_method="manual",
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return {
        "id": record.id,
        "amount": float(record.amount),
        "category": CATEGORY_NAMES.get(record.category, record.category),
        "description": record.description or "",
        "record_date": rec_date.isoformat(),
        "message": "记录成功",
    }


# ==================== 删除账单 ====================

@router.delete("/records/{record_id}")
async def delete_expense_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除一条账单记录"""
    result = await db.execute(
        select(ExpenseRecord).where(
            ExpenseRecord.id == record_id,
            ExpenseRecord.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    await db.delete(record)
    await db.commit()
    return {"message": "已删除"}


# ==================== 账单统计 ====================

@router.get("/stats")
async def expense_stats(
    period: str = Query("month", pattern="^(week|month)$", description="统计周期"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取账单统计数据：分类饼图 + 每日趋势"""
    today = date.today()
    if period == "week":
        since = today - timedelta(days=6)
    else:
        since = today.replace(day=1)

    # 1. 按分类汇总
    cat_q = (
        select(
            ExpenseRecord.category,
            func.sum(ExpenseRecord.amount).label("total"),
            func.count().label("count"),
        )
        .where(
            ExpenseRecord.user_id == current_user.id,
            ExpenseRecord.record_date >= since,
        )
        .group_by(ExpenseRecord.category)
    )
    cat_result = await db.execute(cat_q)
    cat_rows = cat_result.all()

    total_month = 0
    categories = {}
    for cat, total, count in cat_rows:
        name = CATEGORY_NAMES.get(cat, cat)
        categories[name] = {
            "amount": round(float(total), 2),
            "count": count,
        }
        total_month += float(total)

    # 2. 每日趋势
    daily_q = (
        select(
            ExpenseRecord.record_date,
            func.sum(ExpenseRecord.amount).label("total"),
        )
        .where(
            ExpenseRecord.user_id == current_user.id,
            ExpenseRecord.record_date >= since,
        )
        .group_by(ExpenseRecord.record_date)
        .order_by(ExpenseRecord.record_date)
    )
    daily_result = await db.execute(daily_q)
    daily_rows = daily_result.all()

    daily_trend = []
    for d, total in daily_rows:
        daily_trend.append({
            "date": d.isoformat(),
            "amount": round(float(total), 2),
        })

    return {
        "total_month": round(total_month, 2),
        "categories": categories,
        "daily_trend": daily_trend,
    }


# ==================== OCR 识图记账 ====================

class OcrUpload(BaseModel):
    image_base64: str = Field(..., description="图片 base64 编码（可含 data:image 前缀）")
    save: bool = Field(default=False, description="是否直接保存记录（false=仅返回识别结果，供用户核对后手动保存）")

@router.post("/ocr")
async def ocr_expense(
    body: OcrUpload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """拍照识别账单（Qwen VL），可选是否自动保存"""
    if not qwen_vl.is_configured:
        return {
            "success": False,
            "message": "Qwen VL 未配置（请在 .env 中填写 QWEN_API_KEY），请手动录入",
        }

    # 构建 data URL
    if body.image_base64.startswith("data:"):
        image_url = body.image_base64
    else:
        image_url = f"data:image;base64,{body.image_base64}"

    result, error = await qwen_vl.parse_receipt(image_url)
    if error:
        return {"success": False, "message": f"OCR 识别失败: {error}"}
    if not result:
        return {"success": False, "message": "未能识别有效消费信息，请手动录入"}

    amount = float(result.get("amount", 0))
    category = result.get("category", "food")
    description = result.get("description", "")

    if amount <= 0:
        return {"success": False, "message": "未能识别有效金额，请手动录入"}

    # 验证分类
    if category not in CATEGORY_NAMES:
        category = "food"

    # 仅解析模式：返回识别结果，不保存（用户核对后通过 POST /records 保存）
    parsed = {
        "success": True,
        "amount": amount,
        "category": category,
        "category_label": CATEGORY_NAMES.get(category, category),
        "description": (description or "")[:500],
    }
    if not body.save:
        return parsed

    # 自动保存模式
    record = ExpenseRecord(
        user_id=current_user.id,
        amount=amount,
        category=category,
        description=description[:500] if description else None,
        record_date=date.today(),
        input_method="ocr",
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return {
        **parsed,
        "id": record.id,
        "record_date": record.record_date.isoformat(),
        "message": "OCR 识别成功",
    }
