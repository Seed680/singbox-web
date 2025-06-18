#!/bin/bash

# Singbox Web 系统服务卸载脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Singbox Web 系统服务卸载脚本 ===${NC}"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ 请使用root权限运行此脚本${NC}"
    echo "使用方法: sudo ./uninstall-service.sh"
    exit 1
fi

SERVICE_NAME="singbox-web"

# 检查服务是否存在
if [ ! -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
    echo -e "${YELLOW}⚠️  服务未安装${NC}"
    exit 0
fi

# 停止服务
if systemctl is-active --quiet $SERVICE_NAME; then
    echo -e "${YELLOW}⏹️  停止服务...${NC}"
    systemctl stop $SERVICE_NAME
fi

# 禁用服务
if systemctl is-enabled --quiet $SERVICE_NAME; then
    echo -e "${YELLOW}❌ 禁用开机自启动...${NC}"
    systemctl disable $SERVICE_NAME
fi

# 删除服务文件
echo -e "${BLUE}🗑️  删除服务文件...${NC}"
rm -f /etc/systemd/system/$SERVICE_NAME.service

# 重新加载systemd
echo -e "${BLUE}🔄 重新加载 systemd...${NC}"
systemctl daemon-reload
systemctl reset-failed

echo -e "${GREEN}✅ 服务卸载完成！${NC}"
echo -e "${YELLOW}📋 注意: 应用程序文件未被删除，只是移除了系统服务${NC}" 