"""
Pytest全局配置文件
所有测试共享的fixtures和配置
"""

import sys
from pathlib import Path

# 将项目根目录添加到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入fixtures目录中的所有fixtures
pytest_plugins = ['tests.fixtures.conftest']
