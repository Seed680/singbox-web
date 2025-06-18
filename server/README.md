# SingBox Web 后端服务

## 安装依赖

```bash
cd server
npm install
```

## 启动服务

开发模式（支持热重载）：
```bash
npm run dev
```

生产模式：
```bash
npm start
```

服务将在 http://localhost:3001 启动

## API 接口

- GET `/api/config` - 获取所有配置
- POST `/api/subscription` - 保存订阅
- DELETE `/api/subscription/:name` - 删除订阅
- POST `/api/filter` - 保存过滤器
- DELETE `/api/filter/:name` - 删除过滤器
- POST `/api/extra-outbounds` - 保存额外出站配置
- POST `/api/update-subscriptions` - 手动更新所有订阅

## 配置文件

配置保存在 `subscribe_config.json` 文件中，格式如下：

```json
{
  "subscriptions": [],
  "filters": [],
  "ex_outbounds": []
}
``` 