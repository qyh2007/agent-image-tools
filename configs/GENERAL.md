# General Environment Setup

> For users running standard Claude Code (without ECC ecosystem).

## Prerequisites

- Claude Code installed and configured
- Python 3.10+ on your `PATH`
- API Keys for image services

## Step 1: Install MCP Server

Choose your platform:

```bash
# macOS / Linux
bash mcp-server/setup/install.sh

# Windows (PowerShell)
.\mcp-server\setup\install.ps1
```

The script will:
1. Create a Python virtual environment
2. Install dependencies (`mcp`, `httpx`, `python-dotenv`)
3. Copy `.env.example` to `.env` (first run only)
4. Print your JSON configuration snippet

## Step 2: Configure API Keys

Edit `mcp-server/.env` with your real API keys:

```ini
SILICONFLOW_API_KEY=sk-your-siliconflow-api-key-here
AGNES_API_KEY=sk-your-agnes-api-key-here
```

Where to get keys:

| Service | Purpose | Sign Up |
|---------|---------|---------|
| **SiliconFlow** | Image recognition (VLM) | https://cloud.siliconflow.cn → API Keys |
| **Agnes AI** | Image generation | https://apihub.agnes-ai.com → API Keys |

## Step 3: Register MCP Server with Claude Code

Add the following to your Claude Code config file.

**Global config** (`~/.claude.json` on macOS/Linux, `%USERPROFILE%\.claude.json` on Windows):

```json
{
  "mcpServers": {
    "image-mcp-server": {
      "command": "/path/to/mcp-server/.venv/bin/python",
      "args": ["/path/to/mcp-server/server.py"]
    }
  }
}
```

**Or project-level config** (`.claude.json` in your project root):

```json
{
  "mcpServers": {
    "image-mcp-server": {
      "command": "/path/to/mcp-server/.venv/bin/python",
      "args": ["/path/to/mcp-server/server.py"]
    }
  }
}
```

> **Windows note**: Use `\` as path separator. The Python path will be `\path\to\mcp-server\.venv\Scripts\python.exe`.

### Verify the server

After adding the config, restart Claude Code and test:

**Recognition test:**
```
analyze_image(image_path="https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/300px-PNG_transparency_demonstration_1.png", prompt="What is shown in this image?")
```

**Generation test:**
```
generate_image(prompt="A simple red circle on a white background")
```

If you see "识图未配置" or "生图未配置", double-check your `.env` file has the correct keys.

## Step 4: Install the Skill (Optional but Recommended)

Copy the `SKILL.md` to Claude Code's global skills directory:

```bash
# macOS / Linux
mkdir -p ~/.claude/skills
cp SKILL.md ~/.claude/skills/image-tools/

# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills\image-tools"
Copy-Item SKILL.md "$env:USERPROFILE\.claude\skills\image-tools\"
```

Then in Claude Code, invoke the skill when working with images:

```
/image-tools
```

## Step 5: Customize Models (Optional)

Edit `mcp-server/.env` to change the models:

```ini
# Recognition: stronger OCR
VISION_MODEL=Qwen/Qwen2.5-VL-72B-Instruct

# Generation: try Flux
GENERATION_MODEL=flux-pro
```

See `.env.example` for all available options.

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `❌ 识图未配置` | Missing SiliconFlow API key | Fill `SILICONFLOW_API_KEY` in `.env` |
| `❌ 生图未配置` | Missing Agnes AI API key | Fill `AGNES_API_KEY` in `.env` |
| `Connection refused` | Python path wrong | Check `command` in `claude.json` points to venv python |
| `ModuleNotFoundError` | Dependencies not installed | Run `pip install -r requirements.txt` |
| Tool not found in Claude | MCP server not registered | Verify `mcpServers` entry in `.claude.json` |
