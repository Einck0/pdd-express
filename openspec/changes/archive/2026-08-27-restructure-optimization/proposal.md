# 重构优化：pdd-express

## Why

审查确认项目分层与配置管理整体健康，但存在两个高危安全/稳定性缺陷：登录 token 实质是明文 openid（微信生态内并非秘密），且 PUT /cookies 仅受此弱保护却能整体替换全局凭据；上游包裹查询请求无 timeout，单次挂起可拖垮全部 Flask worker。另有一处「配置即状态」耦合：运行时把 cookie 回写进 .env，多线程无锁并发写有损坏风险。

## What Changes

- **BREAKING**（对 API 消费者透明，对攻击面收窄）：token 改为 HMAC 签名带过期时间（标准库实现，不引 JWT 库）；PUT /cookies 额外要求独立管理密钥
- package_service 上游请求补 `timeout=(5, 15)`；异常改自定义 PackageQueryError
- cookie 运行时状态落库（kv 表），删除 .env 回写逻辑；.env 只留启动凭据
- 生产服务器换 gunicorn（-w 2 --threads 4）；compose 删重复 command 定义——在 cookie 落库之后执行，避免多进程放大竞态
- 小程序端删 api.js 死分支（body.success 旧格式）；关键词长度规则收敛 validators.py 单处并注释业务原因
- 补最小测试集：auth 签发/校验 + cookie 持久化（利用已有 create_app 注入点）

## Capabilities

### New Capabilities

- `auth-token`: 登录令牌的签发与校验契约（HMAC 签名、过期、管理操作权限分离）

### Modified Capabilities

## Impact

- 影响：src/middleware/auth.py、src/routes/{auth,cookies}.py、package_service.py、main.py、Dockerfile、docker-compose.yml、miniProgram/utils/api.js
- 新增：DB kv 表、gunicorn 依赖
- 不变：小程序端调用方式（token 不透明）、数据库三后端架构、bind-mount 布局
- 风险控制：pdd.db/.env/logs 为 bind mount 绝不动；先落库改造再上 gunicorn 多进程
