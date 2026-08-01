"""全站通用速率限制（内存实现，修复 H5）

- 基于内存 deque 记录请求时间戳，窗口滑动计数
- 支持按客户端 IP 或按用户 ID 限速
- 单机开发/小型部署足够；多实例部署建议换 Redis 实现
"""

from collections import defaultdict, deque
import functools
import time

from fastapi import HTTPException, Request

_histories: dict[str, deque] = defaultdict(deque)


def _check(key: str, limit: int, window: int) -> bool:
    """滑动窗口限速：窗口内已请求 >= limit 则拒绝"""
    now = time.time()
    q = _histories[key]
    while q and q[0] < now - window:
        q.popleft()
    if len(q) >= limit:
        return False
    q.append(now)
    return True


def _extract_ip(request: Request | None) -> str:
    return request.client.host if (request and request.client) else "unknown"


def rate_limit(prefix: str, limit: int, window: int = 60, use_user: bool = False):
    """限速装饰器。

    - use_user=False：按客户端 IP 限速（key = {prefix}:ip:{ip}）
    - use_user=True：按 current_user.id 限速（key = {prefix}:user:{id}），
      需路由函数有 current_user 参数（FastAPI Depends 注入）
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request")
            if request is None:
                for a in args:
                    if isinstance(a, Request):
                        request = a
                        break
            if use_user:
                user = kwargs.get("current_user")
                key_id = str(getattr(user, "id", "anon"))
                key = f"{prefix}:user:{key_id}"
            else:
                key = f"{prefix}:ip:{_extract_ip(request)}"
            if not _check(key, limit, window):
                raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")
            return await func(*args, **kwargs)
        return wrapper
    return decorator
