"""认证模块 - API 路由"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_current_user
from src.auth import schemas, service
from src.auth.models import User

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=schemas.TokenResponse)
async def register(data: schemas.UserRegister, db: AsyncSession = Depends(get_db)):
    """邮箱注册"""
    # 检查邮箱是否已注册
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该邮箱已注册")

    user = await service.create_user(db, data.email, data.password, data.nickname)
    token = service.create_access_token(user.id)
    return schemas.TokenResponse(
        access_token=token,
        user=schemas.UserOut.model_validate(user),
    )


@router.post("/login", response_model=schemas.TokenResponse)
async def login(data: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    """邮箱登录"""
    user = await service.authenticate_user(db, data.email, data.password)
    if user is None:
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    token = service.create_access_token(user.id)
    return schemas.TokenResponse(
        access_token=token,
        user=schemas.UserOut.model_validate(user),
    )


@router.post("/send-code")
async def send_code(data: schemas.SendCode, db: AsyncSession = Depends(get_db)):
    """发送邮箱验证码"""
    code = await service.save_verification_code(db, data.email)

    from src.services.email import email_service
    if email_service.is_configured:
        import asyncio
        success = await asyncio.to_thread(
            email_service.send_verification_code, data.email, code
        )
        if success:
            return {"message": "验证码已发送到您的邮箱"}
        else:
            raise HTTPException(status_code=500, detail="邮件发送失败，请确认 SMTP 配置正确")

    # 降级：未配置 SMTP 时打印到控制台
    print(f"\n{'='*50}")
    print(f"[验证码] 邮箱: {data.email} → 验证码: {code}")
    print(f"{'='*50}\n")
    return {"message": "验证码已发送（SMTP 未配置，请查看控制台）", "code": code}


@router.post("/verify-email")
async def verify_email(data: schemas.VerifyCode, db: AsyncSession = Depends(get_db)):
    """验证邮箱"""
    ok = await service.verify_email_code(db, data.email, data.code)
    if not ok:
        raise HTTPException(status_code=400, detail="验证码错误或已过期")
    return {"message": "邮箱验证成功"}


@router.get("/me", response_model=schemas.UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return schemas.UserOut.model_validate(current_user)


@router.put("/profile", response_model=schemas.UserOut)
async def update_profile(
    data: schemas.UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """修改个人资料"""
    if data.nickname is not None:
        current_user.nickname = data.nickname
    if data.avatar_url is not None:
        current_user.avatar_url = data.avatar_url
    await db.flush()
    await db.refresh(current_user)
    return schemas.UserOut.model_validate(current_user)
