# Gunicorn 配置文件

import multiprocessing
import os

# 服务器绑定
bind = "0.0.0.0:3001"

# 工作进程数（建议为CPU核心数的2倍+1）
workers = multiprocessing.cpu_count() * 2 + 1

# 工作进程类型（gevent用于异步I/O，适合处理大量并发请求）
worker_class = "gevent"

# 每个worker的连接数
worker_connections = 1000

# 工作进程最大请求数（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 100

# 超时设置
timeout = 120
keepalive = 2

# 进程名称
proc_name = "singbox-web"

# 日志配置
accesslog = "-"  # 输出到stdout
errorlog = "-"   # 输出到stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 日志级别
loglevel = "info"

# 预加载应用（提高性能）
preload_app = True

# 守护进程（设为False，让systemd管理）
daemon = False

# PID文件
pidfile = "/tmp/singbox-web.pid"

# 用户和组（如果需要的话）
# user = "root"
# group = "root"

# 启动时的钩子函数
def on_starting(server):
    server.log.info("Starting Singbox Web Management Panel...")

def on_reload(server):
    server.log.info("Reloading Singbox Web Management Panel...")

def worker_int(worker):
    worker.log.info("Worker received INT or QUIT signal")

def on_exit(server):
    server.log.info("Shutting down Singbox Web Management Panel...") 