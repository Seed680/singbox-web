#!/bin/bash

# Singbox Web 生产环境启动脚本

echo "启动 Singbox Web 管理面板..."

# 检查是否在正确的目录
if [ ! -f "server/api.py" ]; then
    echo "错误: 请在 singbox-web 目录下运行此脚本"
    exit 1
fi

# 检查静态文件是否存在
if [ ! -d "server/static" ]; then
    echo "⚠️  检测到前端未构建，正在自动构建..."
    ./build.sh
    if [ $? -ne 0 ]; then
        echo "❌ 前端构建失败，请手动运行 ./build.sh"
        exit 1
    fi
fi

echo "🚀 启动后端服务..."
cd server

# 检查并激活虚拟环境
VENV_PATH="venv/bin/activate"
if [ -f "$VENV_PATH" ]; then
    echo "📦 激活虚拟环境 (./server/venv)..."
    source "$VENV_PATH"
else
    echo "❌ 错误: 未在 ./server/venv 目录下找到虚拟环境!"
    echo "   请按照以下步骤创建:"
    echo "   1. cd server"
    echo "   2. python3 -m venv venv"
    echo "   3. source venv/bin/activate"
    echo "   4. pip install -r requirements.txt"
    echo "   5. cd .."
    exit 1
fi

# 检查是否安装了gunicorn
if command -v gunicorn &> /dev/null; then
    echo "🔥 使用 Gunicorn 生产服务器启动..."
    echo "📋 配置: 多进程 + 异步处理"
    echo "🌐 访问地址: http://0.0.0.0:3001"
    gunicorn -c gunicorn.conf.py wsgi:application
else
    echo "⚠️  未安装 Gunicorn，使用开发服务器..."
    echo "💡 安装 Gunicorn: pip install gunicorn gevent"
    python api.py
fi 