# 🖼️ Claude Image Tools

> Image recognition & generation for Claude Code with non-multimodal third-party models | 为接入非多模态的第三方模型的 Claude Code 赋予图片识别与生成能力

**English** | [中文](README.md)

---

## 📋 Table of Contents

* [Introduction](#-introduction)

* [Features](#-features)

* [How It Works](#-how-it-works)

* [Skill: Behavior Constraints](#-skill-behavior-constraints)

* [Prerequisites](#-prerequisites)

* [Quick Install](#-quick-install)

* [Configuration](#-configuration)

* [Usage](#-usage)

* [Models Used in This Project](#-models-used-in-this-project)

* [FAQ](#-faq)

* [License](#-license)

---

## 📖 Introduction

**Claude Image Tools** is an open-source image toolkit built for Claude Code, consisting of two parts:

1. **MCP Server** — A standard Python MCP service that provides image recognition and generation via API calls

2. **Claude Skill** — A behavior-constraint skill that governs Claude's tool selection and prompt construction when handling images

With just a few steps, your Claude Code can "see" image content and "draw" what you describe.

> ⚠️ **Important**: This project **cannot directly recognize** images you drag-and-drop into a chat session. Claude Code itself is non-multimodal — uploaded images exist only as chat context and never land on the local filesystem, so MCP tools cannot access them. You need to provide an image URL or a local file path to use the recognition feature.

---

## ✨ Features

| Capability | Description |
|-----------|-------------|
| 🔍 **Image Recognition** | Describe image content, OCR text extraction, object detection, scene analysis, UI inspection |
| 🎨 **Text-to-Image** | Generate images from text descriptions, supporting various styles and sizes |
| 🔄 **Image-to-Image** | Style transfer and partial modification based on a reference image |
| 🛡️ **No Hallucination** | Skill enforces Claude to generate strictly from your description — no invented styles, lighting, or details |
| 🔌 **Plug & Play** | Standard MCP protocol, compatible with any Claude Code environment (including ECC) |

---

## 🔧 How It Works

```
┌─────────────────────────────────────────────────────┐
│                    Claude Code                      │
│                                                     │
│   ┌──────────────┐      ┌────────────────────────┐  │
│   │  SKILL.md    │◄────│  /image-tools invoked   │  │
│   │  (behavior)  │     │  (on demand)            │  │
│   └──────┬───────┘      └────────────────────────┘  │
│          │ normalized tool selection + prompt const.│
│          ▼                                          │
│   ┌─────────────────────────────────────────────┐   │
│   │   MCP Server (server.py)                    │   │
│   │                                             │   │
│   │   analyze_image()    generate_image()       │   │
│   │       │                   │                 │   │
│   │       ▼                   ▼                 │   │
│   │   SiliconFlow API     Agnes AI API          │   │
│   │   (Vision VLM)        (Image Gen)           │   │
│   └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

* **Image Recognition**: Encodes an image (URL or local path) to base64, then analyzes it via a SiliconFlow Vision Language Model (VLM)

* **Image Generation**: Sends the prompt to Agnes AI's text-to-image API; if a reference image is provided, performs style transfer

* **Skill Constraints**: Before calling the generation API, the Skill forces Claude to construct prompts using a template, prohibiting any elements the user did not mention

---

## 🎯 Skill: Behavior Constraints

This project includes a **Claude Code Skill** (`SKILL.md`) that defines Claude's behavior when handling images:

| Constraint | Effect |
|-----------|--------|
| Use `analyze_image` only for recognition, never `Read` for viewing images | Correct tool selection |
| Strict prompt construction per template when generating images | Prevents the model from "hallucinating" unspecified styles/lighting/details |
| Never auto-download generated results | Avoids filesystem pollution |

### ⚠️ Important Note About Prompt Construction Rules

The prompt construction rules (Text-to-Image / Image-to-Image templates) in the Skill **are designed for the models used in this project**:

* **Vision Model**: `nex-agi/Nex-N2-Pro` (detail-sensitive, suitable for high-information-density images)

* **Generation Model**: `Agnes Image 2.1 Flash` (high prompt fidelity, no extra embellishment needed)

If you switch to other models (e.g., Flux, DALL-E, Stable Diffusion, etc.), **adjust the prompt construction rules according to the target model's characteristics**. For example:

* Some models need more detailed English prompts to produce ideal results

* Some models handle Chinese prompts better

* Some models have specific keywords that trigger particular styles

The Skill's Prompt Construction Rule is a **reference framework, not dogma** — understand its core principle of "don't invent what the user didn't say" and adapt it to your actual model.

---

## 📦 Prerequisites

* **Claude Code** installed and configured

* **Python 3.10+** (check with `python --version`)

* **Network access** (to reach the model APIs)

---

## 🚀 Quick Install

> **ECC users**: If you use the ECC (Everything Claude Code) plugin ecosystem, MCP server management differs. ECC manages MCP registration differently — please refer to [configs/ECC.md](configs/ECC.md) directly. The steps below are for standard Claude Code environments.

> **💡 Two installation methods:**
>
> **Method 1: Manual install** — Follow the steps below (for users who want to understand the details)
>
> **Method 2: Let Claude Code do it** — After getting the project, simply tell Claude Code:
>
> > *"Read all the files in this repository, then help me install and configure it"*
>
> Claude Code will automatically understand the project structure, create a virtual environment, install dependencies, prompt you for API keys, and guide you through MCP registration.

### Step 1: Get the Project

```bash
git clone https://github.com/qyh2007/agent-image-tools.git
cd agent-image-tools
```

### Step 2: Install MCP Server

Choose your operating system:

**Windows:**

```powershell
.\mcp-server\setup\install.ps1
```

The script will:

1. Create a Python virtual environment (`mcp-server\.venv\`)

2. Install dependencies

3. Copy `.env.example` to `.env`

4. Print the MCP configuration JSON snippet

**macOS / Linux:**

```bash
bash mcp-server/setup/install.sh
```

The script will:

1. Create a Python virtual environment (`mcp-server/.venv/`)

2. Install dependencies (`mcp`, `httpx`, `python-dotenv`)

3. Copy `.env.example` to `.env`

4. Print the MCP configuration JSON snippet

### Step 3: Configure API Keys

Edit `mcp-server/.env` and fill in your real API keys:

```ini
SILICONFLOW_API_KEY=sk-your-siliconflow-api-key-here
AGNES_API_KEY=sk-your-agnes-api-key-here
```

### Step 4: Register with Claude Code

Register the MCP Server in your Claude Code configuration file.

**Global config** (`~/.claude.json` on macOS/Linux, `%USERPROFILE%\.claude.json` on Windows):

```json
{
  "mcpServers": {
    "image-mcp-server": {
      "command": "/you/path/to/mcp-server/.venv/bin/python",
      "args": ["/you/path/to/mcp-server/server.py"]
    }
  }
}
```

> **Windows path example:**
>
> ```json
> {
>   "mcpServers": {
>     "image-mcp-server": {
>       "command": "C:\\you\\path\\to\\mcp-server\\.venv\\Scripts\\python.exe",
>       "args": ["C:\\you\\path\\to\\mcp-server\\server.py"]
>     }
>   }
> }
> ```

### Step 5: Install the Skill (Recommended)

```bash
# macOS / Linux
mkdir -p ~/.claude/skills/image-tools
cp SKILL.md ~/.claude/skills/image-tools/

# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills\image-tools"
Copy-Item SKILL.md "$env:USERPROFILE\.claude\skills\image-tools\"
```

### Step 6: Verify Installation

Restart Claude Code and run these tests:

**Recognition test:**

```
analyze_image(image_path="https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/300px-PNG_transparency_demonstration_1.png", prompt="What's in this image?")
```

**Generation test:**

```
generate_image(prompt="A simple red circle on a white background")
```

**Skill test:**

```
/image-tools
```

---

## ⚙️ Configuration

Two configuration guides are provided:

| Document | When to Use |
|----------|-------------|
| [configs/GENERAL.md](configs/GENERAL.md) | Standard Claude Code environment (recommended) |
| [configs/ECC.md](configs/ECC.md) | ECC ecosystem users |

### Environment Variables

All configurable options are in `mcp-server/.env`:

```ini
# ──── Recognition ────
SILICONFLOW_API_KEY=sk-xxx          # API Key (required)
VISION_BASE_URL=https://api.siliconflow.cn/v1    # API endpoint
VISION_MODEL=nex-agi/Nex-N2-Pro     # Vision model (change as needed)

# ──── Generation ────
AGNES_API_KEY=sk-xxx                # API Key (required)
AGNES_BASE_URL=https://apihub.agnes-ai.com/v1    # API endpoint
GENERATION_MODEL=agnes-image-2.1-flash  # Generation model (change as needed)

# ──── Save directory (optional) ────
IMAGE_SAVE_DIR=                     # Leave empty to return URL only, set to auto-download
```

---

## 🎬 Usage

### In Claude Code

**Scenario 1: Look at an image**

```
User: What's in this image? https://example.com/photo.jpg
Claude: Calls analyze_image → returns image analysis

User: Can you analyze my local file D:\images\screenshot1.png?
Claude: Calls Read to verify existence → calls analyze_image for content
```

**Scenario 2: Generate an image**

```
/image-tools
User: Draw a dragon for my D&D campaign
Claude: Constructs prompt per Skill constraints → calls generate_image
```

**Scenario 3: Style transfer**

```
/image-tools
User: Turn this logo into a watercolor version, keep the original shape and layout
Claude: Constructs [watercolor] while preserving [shape and layout] → calls generate_image(with reference)
```

### Before vs After Skill

| | Without Skill | With Skill |
|---|-------------|------------|
| User says | "Draw a dragon" | "Draw a dragon" |
| Prompt | `A majestic dragon, realistic fantasy art, cinematic composition, dramatic lighting, ultra-detailed, glowing runes on its scales, highly detailed 8K` | `A dragon for my D&D campaign` |
| Result | ❌ Hallucinated style/lighting/details | ✅ Only what the user said |

---

## 📌 Models Used in This Project

> Copy the info below when asking an AI assistant to help you configure.

### Vision Recognition Model

| Item | Details |
|------|---------|
| **Model** | `nex-agi/Nex-N2-Pro` |
| **Provider** | SiliconFlow |
| **Capabilities** | Image understanding, OCR, object detection, scene description, UI analysis |
| **Website** | https://www.siliconflow.cn/ |
| **API Type** | OpenAI-compatible |

### Image Generation Model

| Item | Details |
|------|---------|
| **Model** | `agnes-image-2.1-flash` |
| **Provider** | Agnes AI |
| **Capabilities** | Text-to-image, image-to-image (style transfer), high-density image generation |
| **Website** | https://agnes-ai.com/ |
| **Features** | High prompt fidelity, fast, good with Chinese prompts |

---

## ❓ FAQ

<details>
<summary><b>Getting "❌ 识图未配置" (Recognition not configured) error</b></summary>

Check that `SILICONFLOW_API_KEY` in `mcp-server/.env` is filled in correctly:

1. `.env` exists in the `mcp-server/` directory (not `.env.example`)

2. API Key format is correct (starts with `sk-`)

3. Your API account has sufficient balance

</details>

<details>
<summary><b>Getting "❌ 生图未配置" (Generation not configured) error</b></summary>

Check that `AGNES_API_KEY` in `mcp-server/.env` is filled in. You need to obtain this key from the respective service provider.

</details>

<details>
<summary><b>Claude Code can't find analyze_image / generate_image tools</b></summary>

This usually means the MCP Server was not registered correctly. Troubleshoot:

1. Verify the `command` path in `~/.claude.json` points to the correct virtual environment Python

2. Run `python mcp-server/server.py` directly in your terminal to check for errors

3. Restart Claude Code and try again

</details>

<details>
<summary><b>Generated image doesn't match the description</b></summary>

1. Check for typos in your prompt

2. Try adding more key details (but don't invent anything the user didn't say)

3. If Chinese prompts don't work well, try English ones

4. Consider switching to a different generation model

</details>

<details>
<summary><b>How to uninstall?</b></summary>

1. Remove the `image-mcp-server` entry from `~/.claude.json`

2. Delete the `~/.claude/skills/image-tools/` directory

3. Delete the project folder

</details>

---

## 📄 License

This project is open-sourced under the MIT License.

---

> **Note**: This project does not contain any API keys. Keep your `.env` file safe and never commit it to version control.
