"""安全模块单元测试：SSRF 图片 URL 校验"""
import asyncio

from src.services.qwen import is_safe_image_url


def _check(url: str) -> bool:
    return asyncio.run(is_safe_image_url(url))


def test_ssrf_allow_https_public():
    # 用公网 IP 字面量（不依赖外网 DNS 解析），非私有/回环即放行
    assert _check("https://8.8.8.8/img.jpg")
    assert _check("https://1.1.1.1/img.jpg")


def test_ssrf_allow_data_url():
    assert _check("data:image/png;base64,iVBORw0KGgo=")


def test_ssrf_block_http_file():
    assert not _check("http://example.com/img.jpg")
    assert not _check("file:///etc/passwd")


def test_ssrf_block_private_ips():
    assert not _check("https://127.0.0.1/x")
    assert not _check("https://192.168.1.1/x")
    assert not _check("https://10.0.0.1/x")
    assert not _check("https://172.16.5.5/x")
    assert not _check("https://169.254.169.254/latest/meta-data")
    assert not _check("https://localhost/x")


def test_ssrf_block_empty():
    assert not _check("")
    assert not _check(None)
