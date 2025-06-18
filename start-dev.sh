#!/bin/bash

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

# 激活虚拟环境并启动服务
if [ -f "venv/bin/activate" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
    
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
else
    echo "虚拟环境不存在，使用系统Python..."
    if command -v python3 &> /dev/null; then
        python3 api.py
    elif command -v python &> /dev/null; then
        python api.py
    else
        echo "❌ 未找到Python解释器"
        exit 1
    fi
fi 