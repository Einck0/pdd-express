# 设计：pdd-express 重构

## Context

项目已经过一轮良好重构（routes/services/models 分层、Settings 数据类、统一响应格式），凭据入库与 CI 规范。本次只动审查确认的三个真问题 + 两个低风险收尾，不为改而改。部署为 docker compose bind-mount（pdd.db/.env/logs 直挂宿主目录），nginx 反代 express.einck.top→15000。当前上游 40002 为业务层错误，与本次无关。

## Goals / Non-Goals

- Goals：token 可信、凭据写权限分离、上游调用有界、配置与状态解耦
- Non-Goals：不拆分文件结构（粒度已合理）、不动 res.js 反爬脚本、不引入 JWT/ORM 重型依赖、不改小程序端交互流程

## Decisions

### D1. HMAC token 标准库实现
登录成功后签发 `payload.expire + hmac_sha256(secret, payload)` 形式 token，secret 从环境变量注入。require_token 校验签名+过期。openid 不再直接作为令牌暴露。

### D2. 管理密钥分离
PUT /cookies 增加 `X-Admin-Key` 校验（环境变量），与用户 token 正交。小程序现有功能不受影响（它不调这个接口）。

### D3. cookie 状态落库
DB 层加 kv 表（key/value/updated_at）。persist_cookies_to_env 删除，update_env_value 随之清理；.env 只保留启动凭据。顺序上必须在 gunicorn 多进程之前完成。

### D4. gunicorn 替换 dev server
requirements.txt + Dockerfile CMD 改 gunicorn -w 2 --threads 4；compose 的重复 command 删除以 Dockerfile 为准。init_db 幂等已确认，保留在启动链。

## Risks / Trade-offs

- token 格式变更会使旧客户端失效 → 小程序端 token 本就不透明且存 storage，重新登录即恢复；发布时无需迁移
- kv 表依赖三后端兼容 → 复用既有 db 抽象层，SQLite/MySQL/PostgreSQL 均可用简单 kv schema

## Migration Plan

按 tasks 顺序执行；测试先行（利用 create_app 注入点）；每步容器内验证；最后 docker compose rebuild + nginx 冒烟。
