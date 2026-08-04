"""FastAPI 应用入口"""

import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings, check_security_config
from src.init_db import init_db
from src.database import close_db

# ========== 启动安全校验：拒绝不安全的 JWT 密钥 / 管理员密码 ==========
_security_problems = check_security_config(settings)
if _security_problems:
    print("\n".join(["[安全校验失败] " + p for p in _security_problems]))
    print("[安全校验失败] 请编辑 server/.env，为 JWT_SECRET 设置强随机字符串、为 ADMIN_PASSWORD 设置强密码，然后重新启动。")
    print("[安全校验失败] 应用已拒绝启动。")
    sys.exit(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    print("[启动] 正在初始化数据库...")
    await init_db()
    print("[启动] 数据库初始化完成")

    from src.auth.service import init_admin
    from src.database import async_session
    async with async_session() as db:
        await init_admin(db)
        await db.commit()
    print("[启动] 管理员初始化完成")

    # 初始化种子数据
    try:
        from src.seed import seed_all
        async with async_session() as db:
            await seed_all(db)
            await db.commit()
        print("[启动] 种子数据初始化完成")
    except Exception as e:
        print(f"[启动] 种子数据初始化失败（可忽略）: {e}")

    # 初始化向量索引
    try:
        from sqlalchemy import text
        from src.services.vector_store import vector_store
        from src.services.deepseek import deepseek as ds_client
        from src.database import async_session

        async with async_session() as db:
            result = await db.execute(text("SELECT id, name, cuisine, category_id, calories_per_100g, tags FROM foods"))
            rows = result.fetchall()
            cat_result = await db.execute(text("SELECT id, name FROM food_categories"))
            cat_map = {row[0]: row[1] for row in cat_result.fetchall()}

            foods = []
            for row in rows:
                cat_name = cat_map.get(row[3], "")
                foods.append({
                    "id": row[0], "name": row[1], "cuisine": row[2] or "",
                    "category_id": row[3] or "", "category_name": cat_name,
                    "calories_per_100g": str(row[4]) if row[4] else "",
                    "tags": row[5] or "[]",
                })

            await vector_store.build_index(foods, ds_client.embed)
        print("[启动] RAG 向量索引构建完成")
    except Exception as e:
        print(f"[启动] RAG 索引构建失败（可忽略）: {e}")

    print(f"[启动] Food-Time API 已就绪")
    print(f"[启动] Swagger 文档: http://localhost:8000/docs")

    yield

    # 关闭时
    print("[关闭] 正在断开数据库连接...")
    await close_db()
    print("[关闭] 已关闭")


app = FastAPI(
    title="Food-Time API",
    description="食光记智能饮食助手网站后端",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 注册路由 ==========
from src.auth.router import router as auth_router
from src.food.router import router as food_router
from src.custom_food.router import router as custom_food_router
from src.public_food.router import router as public_food_router
from src.chat.router import router as chat_router
from src.diet.router import router as diet_router
from src.expense.router import router as expense_router
from src.admin.router import router as admin_router

app.include_router(auth_router)
app.include_router(food_router)
app.include_router(custom_food_router)
app.include_router(public_food_router)
app.include_router(chat_router)
app.include_router(diet_router)
app.include_router(expense_router)
app.include_router(admin_router)

# ========== 静态文件（AI 生成菜品图） ==========
from pathlib import Path
from fastapi.staticfiles import StaticFiles

_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
_STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


@app.get("/")
async def root():
    return {
        "service": "Food-Time API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "Food-Time API", "version": "0.1.0"}
