"""《中国居民膳食指南(2022)》成人每日推荐摄入量参考数据

用于 AI 营养建议的**对照基准**（建议由程序对比，AI 只负责组织语言）：
- 能量 / 蛋白质参考值参考《中国居民膳食营养素参考摄入量（DRIs 2023）》成人 18-49 岁
- 食物类推荐量参考《中国居民膳食指南(2022)》

gender 为空（用户未填）时用 DEFAULT 通用成人参考。
"""

# 按性别分的成人每日推荐值
GUIDELINE = {
    "male": {
        "calories": 2250,          # 能量（kcal/日，中等身体活动）
        "protein": 65,             # 蛋白质（g/日，RNI）
        "fat_pct": (20, 30),       # 脂肪供能占比（%）
        "vegetables": (300, 500),  # 蔬菜（g/日）
        "fruit": (200, 350),       # 水果（g/日）
        "dairy": 300,              # 奶及奶制品（ml/日）
        "water": 1700,             # 饮水（ml/日）
    },
    "female": {
        "calories": 1800,
        "protein": 55,
        "fat_pct": (20, 30),
        "vegetables": (300, 500),
        "fruit": (200, 350),
        "dairy": 300,
        "water": 1500,
    },
}

# 性别未知时的通用成人参考（取男女之间的范围）
DEFAULT = {
    "calories": (1800, 2250),
    "protein": (55, 65),
    "fat_pct": (20, 30),
    "vegetables": (300, 500),
    "fruit": (200, 350),
    "dairy": 300,
    "water": (1500, 1700),
}


def get_guideline(gender: str | None) -> dict:
    """按性别返回推荐量；gender 为空返回通用参考"""
    if gender == "male" or gender == "female":
        return GUIDELINE[gender]
    return DEFAULT


def source_note() -> str:
    return "对照基准：《中国居民膳食指南(2022)》与《中国居民膳食营养素参考摄入量（DRIs 2023）》成人推荐量，仅供参考，非医疗诊断。"
