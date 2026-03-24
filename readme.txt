# pdd-express（彻底切换到 .env 配置）

## 配置方式
本项目**不再使用 `config.ini`**。

唯一配置来源：
- 环境变量
- 或项目根目录下的 `.env`

请先复制：
```bash
cp .env.example .env
```

然后填写实际值。

## 初始化数据库
```bash
python3 init_db.py
```

## 如果需要迁移旧备份库中的手机号数据
```bash
python3 migrate_phones.py
```

## 启动服务
```bash
python3 main.py
```

## 当前结构
- `main.py`：接口入口
- `settings.py`：配置加载（只认 `.env` / 环境变量）
- `database.py`：数据库连接管理
- `repository.py`：数据访问层
- `user_service.py`：业务服务层
- `PackageService.py`：包裹查询服务
- `init_db.py`：初始化数据库结构
- `migrate_phones.py`：旧数据迁移脚本
- `REFACTOR_NOTES.md`：重构学习笔记

## 说明
这是备份项目，已按“可大胆重构”的方式处理：
- 不再兼容 `config.ini`
- 不再依赖 `user_phone_map.phones` 作为正式结构
- 新结构以 `users` + `user_phones` 为准
