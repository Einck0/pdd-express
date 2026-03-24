# pdd-express

[English](./README.md) | [中文](./README.zh-CN.md)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-black)
![Version](https://img.shields.io/badge/version-1.0-brightgreen)
![SQLite](https://img.shields.io/badge/database-SQLite-07405E)
![OpenClaw](https://img.shields.io/badge/Acknowledgement-OpenClaw-6f42c1)

`pdd-express` 是一个基于 Flask 的轻量级后端服务，主要用于管理用户手机号绑定关系，并提供 PDD 快递/包裹查询相关能力。

## 项目简介

这个项目当前具备以下能力：

- 基于 `wxid` 管理用户手机号
- 查询包裹信息
- 提供微信登录接口
- 使用 SQLite 存储本地数据
- 使用 `.env` 管理配置
- 使用标准库 `logging` 记录日志
- 提供数据库初始化与迁移脚本

## 快速开始

### 1）克隆项目

```bash
git clone git@github.com:Einck0/pdd-express.git
cd pdd-express
```

### 2）创建配置文件

```bash
cp .env.example .env
```

然后按需要修改 `.env`。

### 3）创建 Python 环境并安装依赖

使用 `uv`：

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

或使用 Python 自带 `venv`：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4）初始化数据库

```bash
python3 src/init_db.py
```

### 5）本地运行

```bash
python3 src/main.py
```

默认本地端口：
- `5000`

### 6）Docker（可选）

```bash
docker compose up --build
```

Docker 映射端口：
- 宿主机 `15000` -> 容器内 `5000`

## 项目结构

```text
pdd-express/
├── src/
│   ├── main.py
│   ├── settings.py
│   ├── logging_config.py
│   ├── database.py
│   ├── repository.py
│   ├── user_service.py
│   ├── PackageService.py
│   ├── init_db.py
│   └── migrate_phones.py
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── README.md
├── README.zh-CN.md
├── VERSIONED_NOTES.md
└── CLEANUP_NOTES.md
```

## 配置说明

项目使用 `.env` 作为主要配置来源。

示例：

```env
PDD_APP_HOST=0.0.0.0
PDD_APP_PORT=5000
PDD_APP_DEBUG=false
PDD_API_PREFIX=/express
PDD_WECHAT_APPID=
PDD_WECHAT_SECRET=
PDD_SQLITE_DATABASE_DIR=./
PDD_SQLITE_DATABASE_NAME=pdd.db
PDD_MOBILE=
PDD_ENCRYPTED_PASSWORD=
PDD_COOKIE_STRING=
PDD_USER_AGENT=Mozilla/5.0 ...
```

## 数据库说明

初始化数据库结构：

```bash
python3 src/init_db.py
```

如果你有旧数据需要迁移：

```bash
python3 src/migrate_phones.py
```

## API 概览

基础前缀：

```text
/express
```

### 手机号接口
- `GET /express/phones/<wxid>`
- `POST /express/phones/<wxid>`
- `PUT /express/phones/<wxid>`
- `DELETE /express/phones/<wxid>`

### 包裹接口
- `POST /express/package/<wxid>`
- `GET /express/package/<wxid>`

### 登录接口
- `POST /express/wxlogin`

## 致谢

感谢 **OpenClaw** 项目提供的 Agent 工作流与环境支持，这对本项目的整理和重构有直接帮助。

- OpenClaw: <https://github.com/openclaw/openclaw>
- Docs: <https://docs.openclaw.ai>
