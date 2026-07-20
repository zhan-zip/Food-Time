"""FastAPI 应用入口"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.init_db import init_db
from app.database import close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    print("[启动] 正在初始化数据库...")
    await init_db()
    print("[启动] 数据库初始化完成")

    from app.auth.service import init_admin
    from app.database import async_session
    async with async_session() as db:
        await init_admin(db)
        await db.commit()
    print("[启动] 管理员初始化完成")

    # 初始化种子数据
    try:
        from app.seed import seed_all
        async with async_session() as db:
            await seed_all(db)
            await db.commit()
        print("[启动] 种子数据初始化完成")
    except Exception as e:
        print(f"[启动] 种子数据初始化失败（可忽略）: {e}")

    print(f"[启动] Food-Time API 已就绪")
    print(f"[启动] Swagger 文档: http://localhost:8000/docs")

    yield

    # 关闭时
    print("[关闭] 正在断开数据库连接...")
    await close_db()
    print("[关闭] 已关闭")


app = FastAPI(
    title="Food-Time API",
    description="智能饮食辅助 Web 应用后端",
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
from app.auth.router import router as auth_router
from app.food.router import router as food_router
from app.custom_food.router import router as custom_food_router
from app.public_food.router import router as public_food_router
from app.chat.router import router as chat_router
from app.diet.router import router as diet_router
from app.expense.router import router as expense_router
from app.admin.router import router as admin_router

app.include_router(auth_router)
app.include_router(food_router)
app.include_router(custom_food_router)
app.include_router(public_food_router)
app.include_router(chat_router)
app.include_router(diet_router)
app.include_router(expense_router)
app.include_router(admin_router)


@app.get("/")
async def root():
    return {
        "app": "Food-Time API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": "Food-Time API", "version": "0.1.0"}
