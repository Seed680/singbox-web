#!/bin/bash

# Singbox Web 系统服务安装脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Singbox Web 系统服务安装脚本 ===${NC}"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ 请使用root权限运行此脚本${NC}"
    echo "使用方法: sudo ./install-service.sh"
    exit 1
fi

# 获取当前目录的绝对路径
CURRENT_DIR=$(pwd)
PROJECT_DIR="$CURRENT_DIR"
SERVER_DIR="$PROJECT_DIR/server"
SERVICE_NAME="singbox-web"

echo -e "${YELLOW}📁 项目目录: $PROJECT_DIR${NC}"

# 检查必要文件
if [ ! -f "$SERVER_DIR/api.py" ]; then
    echo -e "${RED}❌ 未找到 api.py 文件，请确保在正确的目录下运行${NC}"
    exit 1
fi

if [ ! -d "$SERVER_DIR/venv" ]; then
    echo -e "${RED}❌ 未找到虚拟环境，请先创建虚拟环境${NC}"
    exit 1
fi

if [ ! -f "singbox-web.service" ]; then
    echo -e "${RED}❌ 未找到 singbox-web.service 文件${NC}"
    exit 1
fi

# 停止现有服务（如果存在）
if systemctl is-active --quiet $SERVICE_NAME; then
    echo -e "${YELLOW}⏹️  停止现有服务...${NC}"
    systemctl stop $SERVICE_NAME
fi

# 创建临时服务文件，替换路径
TEMP_SERVICE="/tmp/singbox-web.service"
sed "s|/root/singbox/singbox-web|$PROJECT_DIR|g" singbox-web.service > $TEMP_SERVICE

# 复制服务文件到系统目录
echo -e "${BLUE}📋 安装服务文件...${NC}"
cp $TEMP_SERVICE /etc/systemd/system/singbox-web.service
rm $TEMP_SERVICE

# 设置服务文件权限
chmod 644 /etc/systemd/system/singbox-web.service

# 重新加载systemd
echo -e "${BLUE}🔄 重新加载 systemd...${NC}"
systemctl daemon-reload

# 启用服务（开机自启动）
echo -e "${BLUE}✅ 启用开机自启动...${NC}"
systemctl enable $SERVICE_NAME

# 启动服务
echo -e "${BLUE}🚀 启动服务...${NC}"
systemctl start $SERVICE_NAME

# 等待服务启动
sleep 3

# 检查服务状态
if systemctl is-active --quiet $SERVICE_NAME; then
    echo -e "${GREEN}✅ 服务安装成功并正在运行！${NC}"
    echo -e "${GREEN}🌐 访问地址: http://localhost:3001${NC}"
    echo ""
    echo -e "${BLUE}📋 常用命令:${NC}"
    echo "  查看状态: sudo systemctl status $SERVICE_NAME"
    echo "  启动服务: sudo systemctl start $SERVICE_NAME"
    echo "  停止服务: sudo systemctl stop $SERVICE_NAME"
    echo "  重启服务: sudo systemctl restart $SERVICE_NAME"
    echo "  查看日志: sudo journalctl -u $SERVICE_NAME -f"
    echo "  禁用自启: sudo systemctl disable $SERVICE_NAME"
    echo ""
    echo -e "${YELLOW}📋 服务状态:${NC}"
    systemctl status $SERVICE_NAME --no-pager -l
else
    echo -e "${RED}❌ 服务启动失败！${NC}"
    echo -e "${YELLOW}查看错误日志:${NC}"
    journalctl -u $SERVICE_NAME --no-pager -l
    exit 1
fi 