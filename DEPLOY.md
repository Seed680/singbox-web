# Singbox Web 部署指南

## 快速部署

### 一键启动
```bash
# 进入项目目录
cd singbox-web

# 一键启动（自动构建前端并启动后端）
./start.sh
```

### 手动部署
```bash
# 1. 构建前端
./build.sh

# 2. 启动后端
cd server
source venv/bin/activate  # 激活虚拟环境
python api.py
```

## 部署架构

```
前端 (Vue 3) -> 构建 -> 静态文件 -> Flask 提供静态服务
               vite build    server/static/
```

### 文件结构
```
singbox-web/
├── src/              # Vue 前端源码
├── server/           # Flask 后端
│   ├── static/       # 前端构建输出（自动生成）
│   ├── venv/         # Python 虚拟环境
│   ├── api.py        # 主程序
│   └── config.json   # sing-box 配置
├── build.sh          # 前端构建脚本
├── start.sh          # 一键启动脚本
└── package.json      # 前端依赖
```

## 访问地址

- **生产环境**: http://localhost:3001
- **开发环境**: http://localhost:5173 (前端) + http://localhost:3001 (API)

## 生产环境部署

### 系统要求
- Python 3.7+
- Node.js 16+
- Linux/macOS/Windows

### 安装步骤

1. **克隆项目**
```bash
git clone <项目地址>
cd singbox-web
```

2. **安装前端依赖**
```bash
npm install
```

3. **安装后端依赖**
   > **重要**: 请确保在 `server` 目录下执行这些命令。

   ```bash
   # 进入后端目录
   cd server

   # 创建一个名为 venv 的虚拟环境
   python3 -m venv venv

   # 激活虚拟环境
   # (Windows: venv\Scripts\activate)
   source venv/bin/activate

   # 安装所有依赖
   pip install -r requirements.txt
   
   # 完成后返回上级目录
   cd ..
   ```

4. **构建和启动**
```bash
# 方式一：一键启动
./start.sh

# 方式二：分步执行
./build.sh
./start.sh
```

### 生产环境建议

1. **使用 Nginx 代理**（可选）
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

2. **使用 systemd 服务**
```ini
# /etc/systemd/system/singbox-web.service
[Unit]
Description=Singbox Web
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/path/to/singbox-web/server
ExecStart=/path/to/singbox-web/server/venv/bin/python api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl enable singbox-web
sudo systemctl start singbox-web
sudo systemctl status singbox-web
```

3. **后台运行**
```bash
cd server
nohup source venv/bin/activate && python api.py > singbox-web.log 2>&1 &
```

## 开发模式

```bash
# 启动后端
cd server
source venv/bin/activate
python api.py

# 另开终端启动前端开发服务器
cd singbox-web
npm run dev
```

## 故障排除

### 常见问题

1. **端口占用**
```bash
# 检查端口
netstat -tulnp | grep 3001
# 或者
ss -tulnp | grep 3001

# 杀死进程
kill -9 <PID>
```

2. **Python 模块缺失**
```bash
cd server
source venv/bin/activate
pip install flask flask-cors apscheduler psutil requests
```

3. **前端构建失败**
```bash
# 清除 node_modules 重新安装
rm -rf node_modules package-lock.json
npm install
npm run build
```

4. **权限问题**
```bash
chmod +x build.sh start.sh
```

### 日志查看

```bash
# 查看运行日志
tail -f server/singbox-web.log

# 查看系统服务日志
sudo journalctl -u singbox-web -f
```

## 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建前端
./build.sh

# 重启服务
sudo systemctl restart singbox-web
# 或者手动重启
pkill -f api.py
./start.sh
``` 