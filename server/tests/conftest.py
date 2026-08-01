"""pytest 配置：使 tests/ 能导入 server 下的 src 包"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
