# ECC Ecosystem Setup

> For users running Claude Code with the ECC (Everything Claude Code) plugin ecosystem.

## Overview

ECC 接管了 MCP 服务器的注册和管理流程。与标准 Claude Code 需要在 `~/.claude.json` 中手动配置 `mcpServers` 不同，ECC 通过其插件系统自动发现和管理 MCP 服务。

如果你安装了 ECC，请按照本文档的指引操作，**不要**手动编辑 `~/.claude.json` 的 `mcpServers` 字段，否则可能导致 ECC 的管理机制冲突。

## Quick Start

```bash
# 1. Install MCP server (choose your platform)
bash mcp-server/setup/install.sh                           # macOS / Linux
.\mcp-server\setup\install.ps1                              # Windows

# 2. Edit API keys
vim mcp-server/.env

# 3. Copy skill to global skills
mkdir -p ~/.claude/skills/image-tools
cp SKILL.md ~/.claude/skills/image-tools/
```

## MCP Server Registration

ECC 接管了 MCP 服务的注册，因此你**不需要**手动修改 `~/.claude.json`。

### 安装 MCP Server

将 `mcp-server/` 目录复制或链接到 ECC 的 MCP 服务目录：

```bash
# 创建软链接（推荐，便于后续更新拉取）
ln -s /full/path/to/mcp-server ~/.claude/mcp-servers/image-mcp-server
```

或直接复制：

```bash
cp -r mcp-server ~/.claude/mcp-servers/image-mcp-server
```

ECC 会自动发现并注册 `~/.claude/mcp-servers/` 下的 MCP 服务。安装脚本中的安装步骤（创建虚拟环境、安装依赖、配置 `.env`）仍需要正常执行。

## Skill Usage

ECC loads skills from `~/.claude/skills/` just like vanilla Claude Code.

```
/image-tools    # Invoke the image-tools skill
```

## How This Differs from ECC's Built-in Image Rules

If you have the ECC ecosystem installed, you may also have `rules/ecc/common/image-mcp.md` — a rule file that auto-loads on every session and enforces similar constraints. The two coexist:

| | `SKILL.md` (this project) | `image-mcp.md` (ECC rule) |
|--|--------------------------|--------------------------|
| **Loads** | Manually via `/image-tools` | Automatically on every session |
| **Scope** | Prompt construction rules + tool selection | Tool selection constraints only |
| **Dependency** | None | Requires ECC plugin |

Using **both** gives you automatic guardrails (ECC rule) + on-demand detailed guidance (skill).

## Known ECC-Specific Issues

### GBK Encoding on Chinese Windows

If you run Python scripts from the ECC skill-creator pipeline and encounter `UnicodeDecodeError` with `'gbk'` codec:

```bash
# Fix: set UTF-8 mode before running
set PYTHONUTF8=1    # Windows CMD
$env:PYTHONUTF8=1   # Windows PowerShell
PYTHONUTF8=1        # macOS / Linux
```

This is a Windows locale issue, not specific to this project.
