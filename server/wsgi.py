#!/usr/bin/env python3
"""
WSGI 入口文件 - 用于生产环境部署
"""

import os
import sys

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from api import app

# 这是WSGI应用入口
application = app

if __name__ == "__main__":
    # 直接运行时使用开发服务器
    app.run(host='0.0.0.0', port=3001, debug=False) 