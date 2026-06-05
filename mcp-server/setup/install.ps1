# ═══════════════════════════════════════════════════════════════════
# image-tools — MCP Server 安装脚本 (Windows PowerShell)
# ═══════════════════════════════════════════════════════════════════

$MCP_DIR = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$PROJECT_ROOT = Split-Path -Parent $MCP_DIR

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " image-tools — MCP Server 安装" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# ── 1. 检查 Python ──
$PYTHON = $null
foreach ($cmd in @("python3", "python")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "(\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            if ($major -ge 3 -and $minor -ge 10) {
                $PYTHON = $cmd
                break
            }
        }
    } catch {}
}

if (-not $PYTHON) {
    Write-Host "❌ 需要 Python 3.10+，请先安装: https://python.org" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python: $(& $PYTHON --version)" -ForegroundColor Green

# ── 2. 创建虚拟环境 ──
$VENV_DIR = Join-Path $MCP_DIR ".venv"
if (-not (Test-Path $VENV_DIR)) {
    Write-Host "🔧 创建虚拟环境..." -ForegroundColor Yellow
    & $PYTHON -m venv $VENV_DIR
}
Write-Host "✅ 虚拟环境: $VENV_DIR" -ForegroundColor Green

# ── 3. 安装依赖 ──
$PIP = Join-Path $VENV_DIR "Scripts\pip"
Write-Host "🔧 安装依赖..." -ForegroundColor Yellow
& $PIP install -q -r (Join-Path $MCP_DIR "requirements.txt")
Write-Host "✅ 依赖安装完成" -ForegroundColor Green

# ── 4. 检查 .env ──
$ENV_FILE = Join-Path $MCP_DIR ".env"
if (-not (Test-Path $ENV_FILE)) {
    Write-Host "📝 创建 .env 配置文件..." -ForegroundColor Yellow
    Copy-Item (Join-Path $MCP_DIR ".env.example") $ENV_FILE
    Write-Host ""
    Write-Host "⚠️  请编辑 $ENV_FILE，填入你的 API Key:" -ForegroundColor Yellow
    Write-Host "    - SILICONFLOW_API_KEY (硅基流动, 识图)"
    Write-Host "    - AGNES_API_KEY (Agnes AI, 生图)"
    Write-Host ""
} else {
    Write-Host "✅ .env 已存在" -ForegroundColor Green
}

# ── 5. 输出路径 ──
$SERVER_PATH = Join-Path $MCP_DIR "server.py"
$PYTHON_PATH = Join-Path $VENV_DIR "Scripts\python"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " ✅ 安装完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "MCP Server 路径:" -ForegroundColor White
Write-Host "  $SERVER_PATH" -ForegroundColor Gray
Write-Host ""
Write-Host "虚拟环境 Python:" -ForegroundColor White
Write-Host "  $PYTHON_PATH" -ForegroundColor Gray
Write-Host ""
Write-Host "下一步配置:" -ForegroundColor White
Write-Host "  将以下 MCP 配置写入你的 Claude Code 配置文件:" -ForegroundColor White
Write-Host "  (全局: ~\.claude.json  或  项目: .claude.json)" -ForegroundColor White
Write-Host ""
Write-Host (@"
{
  "mcpServers": {
    "image-mcp-server": {
      "command": "$PYTHON_PATH",
      "args": ["$SERVER_PATH"]
    }
  }
}
"@) -ForegroundColor Cyan
Write-Host ""
Write-Host "详细配置指南见: " -NoNewline; Write-Host "$PROJECT_ROOT\configs\" -ForegroundColor Cyan
Write-Host "Skill 文件:     " -NoNewline; Write-Host "$PROJECT_ROOT\SKILL.md" -ForegroundColor Cyan
