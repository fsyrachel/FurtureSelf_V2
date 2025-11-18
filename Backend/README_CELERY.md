# Celery Worker 启动指南

## 问题说明

在 Windows 上运行 Celery 时，默认的 `prefork` pool 不被支持，会导致任务执行错误：
```
ValueError: not enough values to unpack (expected 3, got 0)
```

## 解决方案

### 方法 1：使用 solo pool（推荐）

```bash
celery -A app.core.celery_app worker --loglevel=info --pool=solo
```

### 方法 2：使用 gevent pool

首先安装 gevent：
```bash
pip install gevent
```

然后启动：
```bash
celery -A app.core.celery_app worker --loglevel=info --pool=gevent
```

### 方法 3：使用提供的批处理脚本

直接双击运行 `start_worker.bat`

## 验证 Worker 是否正常

启动后应该看到：
```
[2025-11-16 17:03:47,733: INFO/MainProcess] celery@YOUR-COMPUTER ready.
```

并且没有 `ValueError` 错误。

## 测试任务

提交一封信件后，检查 worker 日志，应该看到：
```
F4.3 (Worker): 收到任务! LetterID: xxx, UserID: xxx
```

## 常见问题

### Q: 仍然出现 "not enough values to unpack" 错误
**A:** 确保使用了 `--pool=solo` 参数

### Q: 任务一直处于 PENDING 状态
**A:** 检查 Redis 是否正常运行：`redis-cli ping`（应返回 PONG）

### Q: Worker 无法连接到 Redis
**A:** 检查 `.env` 文件中的 `REDIS_URL` 配置

## 开发模式 vs 生产模式

- **开发模式**（Windows）：使用 `--pool=solo`
- **生产模式**（Linux）：使用默认的 `--pool=prefork`（更高性能）



