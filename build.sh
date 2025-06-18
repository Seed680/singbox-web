#!/bin/bash

echo "开始构建 Singbox Web 管理面板..."

# 检查是否在正确的目录
if [ ! -f "package.json" ]; then
    echo "错误: 请在 singbox-web 目录下运行此脚本"
    exit 1
fi

# 安装依赖
echo "安装前端依赖..."
npm install

# 构建前端
echo "构建前端项目..."
npm run build

# 检查构建是否成功
if [ -d "server/static" ]; then
    echo "✅ 前端构建成功！"
    echo "📁 静态文件已生成到: server/static/"
    echo ""
    echo "🚀 现在可以启动后端服务:"
    echo "   cd server"
    echo "   python api.py"
    echo ""
    echo "🌐 然后访问: http://localhost:3001"
else
    echo "❌ 前端构建失败，请检查错误信息"
    exit 1
fi 