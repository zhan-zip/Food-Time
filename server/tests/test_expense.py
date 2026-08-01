"""记账模块单元测试：OCR 金额安全解析"""
from src.expense.router import _parse_amount


def test_parse_amount_plain():
    assert _parse_amount(12.5) == 12.5
    assert _parse_amount("28.9") == 28.9


def test_parse_amount_with_units():
    assert _parse_amount("12.50元") == 12.5
    assert _parse_amount("¥35") == 35.0
    assert _parse_amount("约20") == 20.0
    assert _parse_amount("金额约 16.80 元") == 16.8


def test_parse_amount_european_comma():
    assert _parse_amount("12,50") == 12.5


def test_parse_amount_thousands():
    assert _parse_amount("1,234.56") == 1234.56


def test_parse_amount_invalid():
    assert _parse_amount(None) == 0.0
    assert _parse_amount("") == 0.0
    assert _parse_amount("abc") == 0.0
