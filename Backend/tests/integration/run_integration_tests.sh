#!/bin/bash
# Bash 脚本 - Linux/Mac 环境下运行集成测试
# 用法: bash tests/integration/run_integration_tests.sh

set -e  # 遇到错误立即退出

echo "🚀 启动端到端集成测试环境..."
echo ""

# 检查当前目录
if [[ ! $(basename "$PWD") == "Backend" ]]; then
    echo "❌ 错误：请在 Backend 目录下运行此脚本"
    echo "   当前目录: $PWD"
    exit 1
fi

# 检查 Redis 是否运行
echo "📡 检查 Redis 服务..."
if redis-cli ping &>/dev/null; then
    echo "✅ Redis 运行正常"
else
    echo "❌ Redis 未运行，请先启动 Redis"
    echo "   运行: docker-compose up redis -d"
    exit 1
fi

# 检查环境变量
echo "🔍 检查环境配置..."
if [[ -z "$SILICONFLOW_API_KEY" ]]; then
    echo "⚠️  警告：未设置 SILICONFLOW_API_KEY 环境变量"
    echo "   测试可能因 AI 服务调用失败而失败"
fi

# 启动 Celery Worker（后台）
echo "🔧 启动 Celery Worker..."
celery -A app.core.celery_app worker --loglevel=info &
WORKER_PID=$!

echo "✅ Celery Worker 已启动 (PID: $WORKER_PID)"
echo "   等待 Worker 初始化..."
sleep 5

# 清理函数
cleanup() {
    echo ""
    echo "🛑 停止 Celery Worker..."
    kill $WORKER_PID 2>/dev/null || true
    wait $WORKER_PID 2>/dev/null || true
    echo "✅ Celery Worker 已停止"
}

# 设置退出时清理
trap cleanup EXIT

# 运行集成测试
echo ""
echo "🧪 运行集成测试..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

set +e  # 允许测试失败
pytest tests/integration -v -m integration --tb=short
TEST_EXIT_CODE=$?
set -e

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ 所有集成测试通过！"
else
    echo "❌ 部分测试失败，请检查日志"
fi

echo ""
echo "📊 测试运行完成"
exit $TEST_EXIT_CODE



