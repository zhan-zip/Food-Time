"""认证模块单元测试：验证码、启动安全校验"""
from src.auth.service import generate_verification_code
from src.config import Settings, check_security_config


def test_verification_code_is_6_digit_random():
    codes = [generate_verification_code() for _ in range(5)]
    assert all(len(c) == 6 and c.isdigit() for c in codes)
    assert len(set(codes)) == 5  # 随机性


def test_security_config_empty():
    s = Settings(JWT_SECRET="", ADMIN_PASSWORD="", _env_file=None)
    problems = check_security_config(s)
    assert len(problems) == 2
    assert any("JWT_SECRET" in p for p in problems)
    assert any("ADMIN_PASSWORD" in p for p in problems)


def test_security_config_legacy_defaults():
    s = Settings(JWT_SECRET="food-time-dev-secret", ADMIN_PASSWORD="admin123", _env_file=None)
    problems = check_security_config(s)
    assert len(problems) == 2
    assert all("默认值" in p for p in problems)


def test_security_config_safe():
    s = Settings(JWT_SECRET="x" * 40, ADMIN_PASSWORD="StrongPass_2026!", _env_file=None)
    assert check_security_config(s) == []
