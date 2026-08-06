"""账号系统单元测试：密码管理、schemas 校验"""
import asyncio
import pytest
from pydantic import ValidationError

from src.auth.service import hash_password, verify_password, change_password
from src.auth import schemas


def test_hash_and_verify_password():
    h = hash_password('abc123')
    assert verify_password('abc123', h)
    assert not verify_password('wrong', h)


def test_change_password_ok():
    class FakeUser:
        def __init__(self):
            self.password_hash = hash_password('old123')
    u = FakeUser()
    assert asyncio.run(change_password(u, 'old123', 'new123')) is True
    assert verify_password('new123', u.password_hash)


def test_change_password_wrong_old():
    class FakeUser:
        def __init__(self):
            self.password_hash = hash_password('old123')
    u = FakeUser()
    assert asyncio.run(change_password(u, 'wrong', 'new123')) is False
    assert verify_password('old123', u.password_hash)  # 密码未被修改


def test_register_requires_code():
    """注册必须带验证码（schemas 校验）"""
    with pytest.raises(ValidationError):
        schemas.UserRegister(email='a@b.com', password='123456', nickname='x')


def test_reset_password_short_new_password():
    with pytest.raises(ValidationError):
        schemas.ResetPasswordRequest(email='a@b.com', code='123456', new_password='123')


def test_change_password_request_short():
    with pytest.raises(ValidationError):
        schemas.ChangePasswordRequest(old_password='old123', new_password='123')
