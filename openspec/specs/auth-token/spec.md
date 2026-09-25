# auth-token Specification

## Purpose
登录令牌签发与校验的行为契约：令牌不可伪造、有时效；全局凭据写操作与普通用户身份分离，收窄攻击面。

## Requirements

### Requirement: 令牌不可伪造

登录颁发的 token SHALL 包含服务端 HMAC 签名与过期时间；无签名、签名不符或已过期的 token SHALL 被拒绝。

#### Scenario: 伪造 token 被拒
- **WHEN** 请求携带自造的未签名 token（如裸 openid）
- **THEN** 校验失败返回认证错误，不能冒充任何用户

#### Scenario: 过期 token 被拒
- **WHEN** token 超过有效期后被使用
- **THEN** 返回认证过期错误，客户端需重新登录

### Requirement: 凭据写权限分离

替换全局拼多多凭据的管理接口 SHALL 验证独立管理密钥，普通用户 token 不足以致权。

#### Scenario: 普通用户无法改凭据
- **WHEN** 仅持有普通用户 token 的请求调用凭据替换接口
- **THEN** 返回权限错误，服务端凭据不变

### Requirement: 上游调用有界

对拼多多上游的每个 HTTP 请求 SHALL 设置连接与读取超时；上游挂起时请求在有限时间内失败并返回业务错误，不阻塞 worker。

#### Scenario: 上游挂起不拖垮服务
- **WHEN** 上游接口无响应
- **THEN** 请求在超时窗口内失败，其他用户请求不受影响
