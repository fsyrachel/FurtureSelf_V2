@echo off
REM Celery Worker 启动脚本 (Windows)
REM 注意：Windows 上必须使用 --pool=solo 或 --pool=gevent

echo 正在启动 Celery Worker...
echo.

REM 激活虚拟环境（如果有的话）
REM call D:\Anaconda\envs\backend\Scripts\activate.bat

REM 启动 Celery Worker
REM 使用 solo pool（Windows 兼容模式）
celery -A app.core.celery_app worker --loglevel=info --pool=solo

pause



