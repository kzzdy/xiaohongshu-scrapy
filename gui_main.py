#!/usr/bin/env python
"""
小红书爬虫GUI启动脚本

使用方法：
    python gui_main.py

或者直接双击运行（Windows）
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.gui.main_window import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")
