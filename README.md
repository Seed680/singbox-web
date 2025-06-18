# Singbox Web 管理面板

一个基于 Vue 3 + Flask 的 sing-box 配置管理面板。

## 功能特性

- 订阅管理：支持多个订阅源的添加、更新和删除
- 节点过滤：支持包含/排除条件的节点过滤
- 额外出站：支持添加自定义出站节点
- 配置管理：可视化编辑 sing-box 配置文件
- 服务管理：支持启动/停止 sing-box 服务
- 定时任务：支持定时更新订阅和 sing-box

## 快速开始

### 方式一：一键启动（推荐）

```bash
# 进入项目目录
cd singbox-web

# 一键启动（自动构建前端）
./start.sh
```

### 方式二：手动构建

```bash
# 进入项目目录
cd singbox-web

# 构建前端
./build.sh

# 启动后端服务
cd server
python api.py
```

### 方式三：开发模式

> 开发模式用于代码调试和功能开发，具有热重载功能。

1.  **准备后端环境 (首次运行需要)**
    ```bash
    # 1. 进入 server 目录
    cd singbox-web/server

    # 2. 创建并激活虚拟环境
    python3 -m venv venv
    source venv/bin/activate

    # 3. 安装依赖
    pip install -r requirements.txt
    ```

2.  **启动后端服务**
    ```bash
    # (确保已在 server 目录并激活了 venv)
    python api.py
    ```

3.  **启动前端开发服务器**
    ```bash
    # (另开一个终端)
    cd singbox-web
    npm install
    npm run dev
    ```

## 访问地址

- 生产模式：http://localhost:3001
- 开发模式：http://localhost:5173（前端）+ http://localhost:3001（后端API）

## 部署说明

1. 生产环境只需要启动后端服务，前端已构建为静态文件
2. 前端构建文件位于 `server/static/` 目录
3. 后端会自动提供静态文件服务，无需额外配置 nginx 等

## 项目结构

```
singbox-web/
├── src/              # Vue 前端源码
├── server/           # Flask 后端
│   ├── static/       # 前端构建输出目录
│   ├── api.py        # 主程序
│   ├── config.json   # sing-box 配置
│   └── ...
├── build.sh          # 前端构建脚本
├── start.sh          # 一键启动脚本
└── package.json      # 前端依赖
```

# Vue 3 + Vite

This template should help get you started developing with Vue 3 in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

Learn more about IDE Support for Vue in the [Vue Docs Scaling up Guide](https://vuejs.org/guide/scaling-up/tooling.html#ide-support).
