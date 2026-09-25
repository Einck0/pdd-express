# Tasks: pdd-express restructure-optimization

## 1. 测试先行
- [ ] 1.1 基于 create_app 注入点补 auth 测试：签发/校验/过期/伪造拒绝

## 2. token 加固
- [ ] 2.1 HMAC 签名 token 签发与校验（标准库）；require_token 升级
- [ ] 2.2 PUT /cookies 增加独立管理密钥校验

## 3. 上游调用有界
- [ ] 3.1 get_response 补 timeout=(5,15)；PackageQueryError 自定义异常

## 4. cookie 状态落库
- [ ] 4.1 kv 表 + cookie 读写迁移；删 persist_cookies_to_env/update_env_value
- [ ] 4.2 .env 回写逻辑清理；并发写风险消除

## 5. gunicorn（依赖任务 4 完成）
- [ ] 5.1 requirements + Dockerfile CMD 换 gunicorn -w 2 --threads 4；compose 删重复 command

## 6. 小程序收尾
- [ ] 6.1 api.js 删 body.success 死分支；关键词长度规则收敛 validators.py 并注释原因

## 7. 验证与部署
- [ ] 7.1 容器 rebuild 后健康检查 + 登录/查询冒烟
- [ ] 7.2 nginx 反代链路验证（express.einck.top）
- [ ] 7.3 git commit + push + openspec archive
