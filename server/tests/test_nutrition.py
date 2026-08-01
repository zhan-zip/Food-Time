"""营养模块单元测试：烹饪修正系数"""
from src.diet.router import COOKING_FACTORS, _cooking_factor


def test_cooking_factors_defined():
    assert COOKING_FACTORS["stir-fry"] == 1.20
    assert COOKING_FACTORS["fry"] == 1.50
    assert COOKING_FACTORS["boil"] == 0.90
    assert COOKING_FACTORS["steam"] == 0.95


def test_factor_default_no_tags():
    food = type("Food", (), {"tags": None})()
    assert _cooking_factor(food) == 1.00


def test_factor_default_no_cooking():
    food = type("Food", (), {"tags": {"spicy": "high"}})()
    assert _cooking_factor(food) == 1.00


def test_factor_dict_tags():
    food = type("Food", (), {"tags": {"cooking": "stir-fry"}})()
    assert _cooking_factor(food) == 1.20


def test_factor_string_tags():
    food = type("Food", (), {"tags": '{"cooking":"fry"}'})()
    assert _cooking_factor(food) == 1.50
