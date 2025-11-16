# PowerShell 脚本 - Windows 环境下运行集成测试
# 用法: .\tests\integration\run_integration_tests.ps1

Write-Host "🚀 启动端到端集成测试环境..." -ForegroundColor Green
Write-Host ""

# 检查当前目录
$currentDir = Get-Location
if (-not $currentDir.Path.EndsWith("Backend")) {
    Write-Host "❌ 错误：请在 Backend 目录下运行此脚本" -ForegroundColor Red
    Write-Host "   当前目录: $currentDir" -ForegroundColor Yellow
    exit 1
}

# 检查 Redis 是否运行
Write-Host "📡 检查 Redis 服务..." -ForegroundColor Cyan
try {
    $redisCheck = redis-cli ping 2>$null
    if ($redisCheck -eq "PONG") {
        Write-Host "✅ Redis 运行正常" -ForegroundColor Green
    } else {
        Write-Host "❌ Redis 未运行，请先启动 Redis" -ForegroundColor Red
        Write-Host "   运行: docker-compose up redis -d" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ 无法连接 Redis，请检查服务是否启动" -ForegroundColor Red
    exit 1
}

# 检查环境变量
Write-Host "🔍 检查环境配置..." -ForegroundColor Cyan
if (-not $env:SILICONFLOW_API_KEY) {
    Write-Host "⚠️  警告：未设置 SILICONFLOW_API_KEY 环境变量" -ForegroundColor Yellow
    Write-Host "   测试可能因 AI 服务调用失败而失败" -ForegroundColor Yellow
}

# 启动 Celery Worker（后台）
Write-Host "🔧 启动 Celery Worker..." -ForegroundColor Cyan
$workerJob = Start-Job -ScriptBlock {
    Set-Location $using:currentDir
    celery -A app.core.celery_app worker --loglevel=info --pool=solo
}

Write-Host "✅ Celery Worker 已启动 (Job ID: $($workerJob.Id))" -ForegroundColor Green
Write-Host "   等待 Worker 初始化..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 运行集成测试
Write-Host ""
Write-Host "🧪 运行集成测试..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

try {
    pytest tests/integration -v -m integration --tb=short
    $testExitCode = $LASTEXITCODE
} finally {
    # 停止 Celery Worker
    Write-Host ""
    Write-Host "🛑 停止 Celery Worker..." -ForegroundColor Cyan
    Stop-Job -Job $workerJob
    Remove-Job -Job $workerJob
    Write-Host "✅ Celery Worker 已停止" -ForegroundColor Green
}

Write-Host ""
if ($testExitCode -eq 0) {
    Write-Host "✅ 所有集成测试通过！" -ForegroundColor Green
} else {
    Write-Host "❌ 部分测试失败，请检查日志" -ForegroundColor Red
}

Write-Host ""
Write-Host "📊 测试运行完成" -ForegroundColor Cyan
exit $testExitCode




