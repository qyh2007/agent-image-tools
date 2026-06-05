#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# image-tools — MCP Server 安装脚本 (Linux / macOS)
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$MCP_DIR")"

echo "========================================"
echo " image-tools — MCP Server 安装"
echo "========================================"

# ── 1. 检查 Python ──
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PY_VER="$($cmd --version 2>&1 | grep -oP '\d+\.\d+')"
        MAJOR="${PY_VER%%.*}"
        MINOR="${PY_VER#*.}"
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 10 ]; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "❌ 需要 Python 3.10+, 请先安装: https://python.org"
    exit 1
fi
echo "✅ Python: $($PYTHON --version)"

# ── 2. 创建虚拟环境 ──
VENV_DIR="$MCP_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "🔧 创建虚拟环境..."
    $PYTHON -m venv "$VENV_DIR"
fi
echo "✅ 虚拟环境: $VENV_DIR"

# ── 3. 激活并安装依赖 ──
source "$VENV_DIR/bin/activate"
echo "🔧 安装依赖..."
pip install -q -r "$MCP_DIR/requirements.txt"
echo "✅ 依赖安装完成"

# ── 4. 检查 .env ──
if [ ! -f "$MCP_DIR/.env" ]; then
    echo "📝 创建 .env 配置文件..."
    cp "$MCP_DIR/.env.example" "$MCP_DIR/.env"
    echo ""
    echo "⚠️  请编辑 $MCP_DIR/.env, 填入你的 API Key:"
    echo "    - SILICONFLOW_API_KEY (硅基流动, 识图)"
    echo "    - AGNES_API_KEY (Agnes AI, 生图)"
    echo ""
else
    echo "✅ .env 已存在"
fi

# ── 5. 输出路径 ──
echo ""
echo "========================================"
echo " ✅ 安装完成！"
echo "========================================"
echo ""
echo "MCP Server 路径:"
echo "  $MCP_DIR/server.py"
echo ""
echo "虚拟环境 Python:"
echo "  $VENV_DIR/bin/python"
echo ""
echo "下一步配置:"
echo "  将以下 MCP 配置写入你的 Claude Code 配置文件:"
echo "  ~/.claude.json  (全局) 或  .claude.json (项目)"
echo ""

SERVER_PATH="$MCP_DIR/server.py"
PYTHON_PATH="$VENV_DIR/bin/python"

cat <<EOF
{
  "mcpServers": {
    "image-mcp-server": {
      "command": "$PYTHON_PATH",
      "args": ["$SERVER_PATH"]
    }
  }
}
EOF

echo ""
echo "详细配置指南见: $PROJECT_ROOT/configs/"
echo "Skill 文件:     $PROJECT_ROOT/SKILL.md"
