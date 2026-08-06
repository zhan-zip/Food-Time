"""认证模块 - API 路由"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.dependencies import get_current_user
from src.auth import schemas, service
from src.auth.models import User
from src.rate_limit import rate_limit

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=schemas.TokenResponse)
@rate_limit("register", 5, 60)  # H5：注册 5 次/分钟/IP
async def register(data: schemas.UserRegister, request: Request, db: AsyncSession = Depends(get_db)):
    """邮箱注册（强制校验邮箱验证码，防绕过前端注册任意邮箱）"""
    # 修复 H2：移除"先 SELECT 查重再 INSERT"的 TOCTOU 竞态，
    # 改为直接 INSERT，依赖唯一索引 + IntegrityError 捕获，并发注册返回 400 而非 500。
    from sqlalchemy.exc import IntegrityError
    # 校验验证码：通过则标记已用（create_user 失败时 rollback 回滚，验证码可重用）
    if not await service.validate_registration_code(db, data.email, data.code):
        await db.rollback()
        raise HTTPException(status_code=400, detail="验证码错误或已过期")
    try:
        user = await service.create_user(
            db, data.email, data.password, data.nickname,
            data.avatar_url, data.age, data.gender, data.height_cm, data.weight_kg,
            email_verified=True,
        )
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="该邮箱已注册")
    token = service.create_access_token(user.id)
    return schemas.TokenResponse(
        access_token=token,
        user=schemas.UserOut.model_validate(user),
    )


@router.post("/login", response_model=schemas.TokenResponse)
@rate_limit("login", 5, 60)  # H5：登录 5 次/分钟/IP
async def login(data: schemas.UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
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
@rate_limit("send_code", 1, 60)  # H5：验证码 1 次/分钟/IP（由 M13 内联升级为通用限速）
async def send_code(
    data: schemas.SendCode,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """发送邮箱验证码"""
    code = await service.save_verification_code(db, data.email)
    # 修复 M7：先提交验证码记录，释放 DB 事务，再执行耗时的 SMTP 发送（避免长持有连接/行锁）
    await db.commit()

    from src.services.email import email_service
    if email_service.is_configured:
        import asyncio
        success = await asyncio.to_thread(
            email_service.send_verification_code, data.email, code
        )
        if success:
            return {"message": "验证码已发送到您的邮箱"}
        # 发送失败降级：打印控制台（DEBUG 可继续），避免 SMTP 失效导致功能不可用
        print(f"\n{'='*50}")
        print(f"[验证码-发送失败降级] 邮箱: {data.email} → 验证码: {code}")
        print(f"{'='*50}\n")
        if settings.DEBUG:
            return {"message": "邮件发送失败，验证码已打印到后端控制台（请检查 SMTP 配置）"}
        raise HTTPException(status_code=500, detail="邮件发送失败，请确认 SMTP 配置正确")

    # 降级：未配置 SMTP 时打印到控制台（修复 M6：不再通过 HTTP 返回验证码明文）
    print(f"\n{'='*50}")
    print(f"[验证码] 邮箱: {data.email} → 验证码: {code}")
    print(f"{'='*50}\n")
    if settings.DEBUG:
        return {"message": "验证码已发送（SMTP 未配置，请查看后端控制台）"}
    raise HTTPException(status_code=500, detail="邮件服务未配置，请联系管理员")


@router.post("/verify-email")
async def verify_email(data: schemas.VerifyCode, db: AsyncSession = Depends(get_db)):
    """验证邮箱"""
    ok = await service.verify_email_code(db, data.email, data.code)
    if not ok:
        raise HTTPException(status_code=400, detail="验证码错误或已过期")
    return {"message": "邮箱验证成功"}


@router.post("/forgot-password")
@rate_limit("send_code", 1, 60)  # 复用验证码限速：1 次/分钟/IP
async def forgot_password(data: schemas.ForgotPasswordRequest, request: Request, db: AsyncSession = Depends(get_db)):
    """忘记密码：发送重置验证码"""
    code = await service.save_verification_code(db, data.email)
    await db.commit()

    from src.services.email import email_service
    if email_service.is_configured:
        import asyncio
        success = await asyncio.to_thread(email_service.send_verification_code, data.email, code)
        if success:
            return {"message": "验证码已发送到您的邮箱"}
        # 发送失败降级：打印控制台（DEBUG 可继续），避免 SMTP 失效导致功能不可用
        print(f"\n{'='*50}")
        print(f"[验证码-发送失败降级] 邮箱: {data.email} → 验证码: {code}")
        print(f"{'='*50}\n")
        if settings.DEBUG:
            return {"message": "邮件发送失败，验证码已打印到后端控制台（请检查 SMTP 配置）"}
        raise HTTPException(status_code=500, detail="邮件发送失败，请确认 SMTP 配置正确")

    print(f"\n[验证码] 邮箱: {data.email} → 验证码: {code}\n")
    if settings.DEBUG:
        return {"message": "验证码已发送（SMTP 未配置，请查看后端控制台）"}
    raise HTTPException(status_code=500, detail="邮件服务未配置，请联系管理员")


@router.post("/reset-password")
async def reset_password(data: schemas.ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """忘记密码：验证码 + 新密码重置"""
    if not await service.validate_registration_code(db, data.email, data.code):
        await db.rollback()
        raise HTTPException(status_code=400, detail="验证码错误或已过期")
    ok = await service.reset_password(db, data.email, data.new_password)
    await db.commit()
    if not ok:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"message": "密码已重置，请用新密码登录"}


@router.put("/change-password")
async def change_password(
    data: schemas.ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """修改密码：验证旧密码后更新"""
    ok = await service.change_password(current_user, data.old_password, data.new_password)
    if not ok:
        raise HTTPException(status_code=400, detail="旧密码不正确")
    await db.flush()
    return {"message": "密码已修改"}


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
    """修改个人资料（支持清空档案字段：显式传 null 即置空）"""
    # 修复：用 exclude_unset 区分「未传」与「传 null 清空」，支持清空档案字段
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        if field == "nickname" and value is None:
            continue  # 昵称不允许置空（数据库 NOT NULL）
        setattr(current_user, field, value)
    await db.flush()
    await db.refresh(current_user)
    return schemas.UserOut.model_validate(current_user)
