# pdd-express 快递取件助手

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-black)
![Version](https://img.shields.io/badge/version-3.0.0-brightgreen)
![SQLite](https://img.shields.io/badge/database-SQLite-07405E)

微信小程序 + Flask 后端，绑定号码后自动跟踪快递包裹。

## 功能

- 号码管理：添加 / 删除 / 查询绑定号码
- 包裹查询：按号码自动查询关联包裹
- 搜索：运单号后 5 位 / 全部单号 / 号码
- 微信登录：wx.login + 后端 openid 认证
- Cookie 管理：API 设置和持久化拼多多 cookie

## 快速开始

### 1. 克隆项目

```bash
git clone git@github.com:Einck0/pdd-express.git
cd pdd-express
```

### 2. 创建环境文件

```bash
cp .env.example .env
# 编辑 .env 填入配置
```

### 3. Docker 启动

```bash
docker compose up --build
```

端口映射：宿主机 `15000` → 容器 `5000`

### 本地开发

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 src/init_db.py
python3 src/main.py
```

> ⚠️ 本地运行需要 Node.js（`pyexecjs` 依赖 Node 执行 `src/res.js` 反爬脚本）

## 项目结构

```
pdd-express/
├── src/                        # Flask 后端
│   ├── app.py                  # 应用工厂，注册蓝图
│   ├── config.py               # 配置加载（Settings dataclass）
│   ├── main.py                 # 入口
│   ├── routes/                 # 路由蓝图
│   │   ├── auth.py             # wxlogin
│   │   ├── phones.py           # 号码 CRUD
│   │   ├── packages.py         # 包裹查询
│   │   └── cookies.py          # cookie 管理
│   ├── services/               # 业务逻辑
│   │   ├── package_service.py  # 包裹查询 + anti-content
│   │   ├── user_service.py     # 用户/号码管理
│   │   └── cookie_service.py
│   ├── middleware/
│   │   ├── auth.py             # @require_token 认证装饰器
│   │   └── error_handler.py
│   ├── models/
│   │   └── database.py         # SQLite/MySQL/PostgreSQL
│   ├── utils/
│   │   ├── response.py         # 统一响应格式
│   │   └── validators.py       # 参数校验
│   ├── init_db.py
│   ├── logging_config.py
│   └── res.js                  # anti-content 脚本
├── miniProgram/                # 微信小程序前端
│   ├── config/config.js        # 默认配置（apiBaseUrl 用占位符）
│   ├── utils/api.js            # 统一请求封装
│   ├── pages/index/            # 查件首页
│   └── pages/bindPhone/        # 号码管理页
├── .github/workflows/
│   └── miniprogram-upload.yml  # CI：注入配置 + 上传体验版
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env                        # 运行时配置（不提交）
```

## 配置

通过 `.env` 文件配置：

```env
PDD_APP_HOST=0.0.0.0
PDD_APP_PORT=15000
PDD_API_PREFIX=/express
PDD_WECHAT_APPID=
PDD_WECHAT_SECRET=
PDD_SQLITE_DATABASE_DIR=./
PDD_SQLITE_DATABASE_NAME=pdd.db
PDD_MOBILE=
PDD_ENCRYPTED_PASSWORD=
PDD_COOKIE_STRING=
```

## API

认证方式：`Authorization: Bearer <wxid>`（Header token）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /express/wxlogin | 微信登录，返回 token |
| GET | /express/phones | 获取绑定号码列表 |
| POST | /express/phones | 添加号码 |
| DELETE | /express/phones | 删除号码 |
| GET | /express/package | 查询所有包裹 |
| POST | /express/package | 搜索包裹（keyword） |
| PUT | /express/cookies | 设置 cookie |
| GET | /express/cookies | 查看 cookie keys |
| GET | /health | 健康检查 |

统一响应格式：
```json
{"code": 0, "message": "ok", "data": {...}}
```

## CI/CD

GitHub Actions 自动上传小程序体验版：

- 触发条件：push 到 `dev` 或 `main` 分支，且 `miniProgram/` 目录有变更
- 需要配置 Secrets：`WX_APPID`、`WX_UPLOAD_KEY`、`API_BASE_URL`
- 使用固定 `robot 1` 上传，自动继承体验版

## 致谢

- [OpenClaw](https://github.com/openclaw/openclaw) — AI 代理工作流支持
