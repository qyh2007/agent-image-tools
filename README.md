# 🖼️ Claude Image Tools

> 为接入非多模态的第三方模型的 Claude Code 赋予图片识别与生成能力 | Image recognition & generation for Claude Code

[English](README.en.md) | **中文**

---

## 📋 目录

* [项目简介](#-项目简介)

* [功能特性](#-功能特性)

* [工作原理](#-工作原理)

* [Skill：智能行为约束](#-skill智能行为约束)

* [前置条件](#-前置条件)

* [快速安装](#-快速安装)

* [配置指南](#-配置指南)

* [使用方法](#-使用方法)

* [本项目使用的模型](#-本项目使用的模型)

* [常见问题](#-常见问题)

* [许可](#-许可)

---

## 📖 项目简介

**Claude Image Tools** 是一个为 Claude Code 量身打造的开源图片工具集，包含两大部分：

1. **MCP Server** — 一个标准化的 Python MCP 服务，通过 API 调用实现图片识别与图片生成

2. **Claude Skill** — 一个行为约束技能，规范 Claude 在处理图片时的工具选择和提示词构造行为

只需几步配置，你的 Claude Code 就能"看懂"图片内容、"画出"你想要的画面。

> ⚠️ **重要说明**：本项目**无法直接识别**你在会话中拖入/上传的图片。因为模型本身是非多模态的，你上传的图片仅作为聊天上下文存在，不会落到本地文件系统，MCP 工具无法访问。需要使用图片的 URL 或本地文件路径来调用识别功能。

---

## ✨ 功能特性

| 能力          | 说明                                       |
| ----------- | ---------------------------------------- |
| 🔍 **图片识别** | 描述图片内容、OCR 文字识别、物体检测、场景分析、UI 界面审查        |
| 🎨 **文生图**  | 根据文字描述生成图片，支持多种风格和尺寸                     |
| 🔄 **图生图**  | 以参考图为基础进行风格迁移、局部修改                       |
| 🛡️ **防脑补** | Skill 约束 Claude 严格按照你的描述生图，不擅自添加风格/光影/细节 |
| 🔌 **即插即用** | 标准 MCP 协议，兼容任意 Claude Code 环境（含 ECC）     |

---

## 🔧 工作原理

```
┌─────────────────────────────────────────────────────┐
│                    Claude Code                       │
│                                                      │
│   ┌──────────────┐      ┌────────────────────────┐  │
│   │  SKILL.md     │◄──── │  /image-tools 调起      │  │
│   │  (行为约束)    │      │  (按需调用)              │  │
│   └──────┬───────┘      └────────────────────────┘  │
│          │ 规范化工具选择 + 提示词构造                  │
│          ▼                                            │
│   ┌─────────────────────────────────────────────┐    │
│   │   MCP Server (server.py)                     │    │
│   │                                              │    │
│   │   analyze_image()    generate_image()        │    │
│   │       │                   │                  │    │
│   │       ▼                   ▼                  │    │
│   │   SiliconFlow API     Agnes AI API           │    │
│   │   (识图 VLM)           (生图模型)              │    │
│   └─────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

* **图片识别**：将图片（URL 或本地路径）编码为 base64，通过 SiliconFlow 的视觉语言模型（VLM）进行分析

* **图片生成**：将提示词发送至 Agnes AI 的文生图 API 生成图片；若提供参考图则进行风格迁移

* **Skill 约束**：在调用生图 API 之前，Skill 强制 Claude 按模板构造提示词，禁止添加用户未提及的描述

---

## 🎯 Skill：智能行为约束

项目中附带了一份 **Claude Code Skill**（`SKILL.md`），它定义了 Claude 在图片处理场景中的行为规范：

| 约束                                    | 效果              |
| ------------------------------------- | --------------- |
| 只能用 `analyze_image` 识图，禁止用 `Read` 看图片 | 正确的工具选择         |
| 生图时严格按照模板构造提示词                        | 防止模型"脑补"用户没说的内容 |
| 禁止自动下载生成结果                            | 避免文件系统污染        |

### ⚠️ 关于生图提示词约束的重要说明

Skill 中关于生图提示词构造的规则（Text-to-Image / Image-to-Image 模板）**是适配本项目所使用的视觉模型和生图模型而设计的**：

* **识图模型**：`nex-agi/Nex-N2-Pro`（对细节敏感，适合高密度信息）

* **生图模型**：`Agnes Image 2.1 Flash`（对提示词忠实度高，无需额外润色）

如果你更换了其他模型（如 Flux、DALL-E、Stable Diffusion 等），**建议根据目标模型的特点调整提示词构造规则**。例如：

* 某些模型需要更详细的英文提示词才能达到理想效果

* 某些模型对中文提示词支持更好

* 某些模型有特定的关键词触发特定风格

Skill 的 Prompt Construction Rule 是**参考框架而非铁律** —— 理解其"不脑补用户未提及内容"的核心精神，根据实际使用的模型进行调整。

---

## 📦 前置条件

* **Claude Code** 已安装并配置

* **Python 3.10+**（可在终端执行 `python --version` 检查）

* **网络连接**（需要访问模型的 API）

---

## 🚀 快速安装

> **ECC 用户请注意**：如果你使用了 ECC（Everything Claude Code）插件生态，MCP 服务器的管理方式会有所不同。ECC 接管了 MCP 服务的注册流程，建议直接参考 [configs/ECC.md](configs/ECC.md) 进行配置。以下步骤适用于标准 Claude Code 环境。
>
> **💡 两种安装方式：**
>
> **方式一：手动安装** — 按照下方步骤逐一操作（适合想了解细节的用户）
>
> **方式二：交给 Claude Code** — 获取项目后，直接向 Claude Code 发送以下指令即可：
>
> > *"阅读这个仓库的所有文件，然后帮我完成安装和配置"*
>
> Claude Code 会自动理解项目结构、创建虚拟环境、安装依赖、提示你填入 API Key，并指导你完成 MCP 注册。

### 第一步：获取项目

```bash
git clone https://github.com/qyh2007/agent-image-tools.git
cd agent-image-tools
```

### 第二步：安装 MCP Server

根据你的操作系统选择：

**Windows：**

```powershell
.\mcp-server\setup\install.ps1
```

脚本将自动：

1. 创建 Python 虚拟环境（`mcp-server\.venv\`）

2. 安装依赖包

3. 从 `.env.example` 复制生成 `.env`

4. 打印 MCP 配置 JSON 片段

**macOS / Linux：**

```bash
bash mcp-server/setup/install.sh
```

脚本将自动：

1. 创建 Python 虚拟环境（`mcp-server/.venv/`）

2. 安装依赖包（`mcp`, `httpx`, `python-dotenv`）

3. 从 `.env.example` 复制生成 `.env` 配置文件

4. 打印 MCP 配置 JSON 片段

### 第三步：配置 API Key

编辑 `mcp-server/.env`，填入你的真实 API Key：

```ini
SILICONFLOW_API_KEY=sk-your-siliconflow-api-key-here
AGNES_API_KEY=sk-your-agnes-api-key-here
```

### 第四步：注册到 Claude Code

将 MCP Server 注册到 Claude Code 的配置文件中。

**全局配置**（`~/.claude.json`）：

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

> **Windows 路径示例**：
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

### 第五步：安装 Skill（推荐）

```bash
# macOS / Linux
mkdir -p ~/.claude/skills/image-tools
cp SKILL.md ~/.claude/skills/image-tools/

# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills\image-tools"
Copy-Item SKILL.md "$env:USERPROFILE\.claude\skills\image-tools\"
```

### 第六步：验证安装

重启 Claude Code，依次测试：

**识别测试**：

```
analyze_image(image_path="https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/300px-PNG_transparency_demonstration_1.png", prompt="这张图片里有什么？")
```

**生成测试**：

```
generate_image(prompt="一个简单的红色圆形，白色背景")
```

**Skill 测试**：

```
/image-tools
```

---

## ⚙️ 配置指南

本项目提供两份配置文档：

| 文档                                       | 适用场景                  |
| ---------------------------------------- | --------------------- |
| [configs/GENERAL.md](configs/GENERAL.md) | 标准 Claude Code 环境（推荐） |
| [configs/ECC.md](configs/ECC.md)         | 使用 ECC 生态系统的用户        |

### 模型与环境变量

所有可配置项都在 `mcp-server/.env` 中：

```ini
# ──── 识别配置 ────
SILICONFLOW_API_KEY=sk-xxx          # API Key（必填）
VISION_BASE_URL=https://api.siliconflow.cn/v1    # API 地址
VISION_MODEL=nex-agi/Nex-N2-Pro     # 视觉模型名（按需修改）

# ──── 生成配置 ────
AGNES_API_KEY=sk-xxx                # API Key（必填）
AGNES_BASE_URL=https://apihub.agnes-ai.com/v1    # API 地址
GENERATION_MODEL=agnes-image-2.1-flash  # 生图模型名（按需修改）

# ──── 保存路径（可选）───
IMAGE_SAVE_DIR=                     # 留空只返回 URL，设置后自动下载到本地
```

---

## 🎬 使用方法

### 在 Claude Code 中调用

**场景 1：看一张图片**

```
用户：帮我看一下这张图片 https://example.com/photo.jpg 里有什么
Claude：调用 analyze_image → 返回图片分析结果

用户：分析一下我本地 D:\图片\截图1.png 的内容
Claude：调用 Read 确认文件存在 → 调用 analyze_image 分析内容
```

**场景 2：生成一张图片**

```
/image-tools
用户：帮我画一只龙，给我的 D&D 跑团用
Claude：按 Skill 约束构造提示词 → 调用 generate_image
```

**场景 3：风格迁移**

```
/image-tools
用户：把这个 logo 改成水彩风格，保留原来的形状和布局
Claude：构造 [水彩化] while preserving [形状和布局] → 调用 generate_image(with reference)
```

### Skill 作用前后对比

|     | 无 Skill                                                                                                                                               | 有 Skill                        |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| 用户说 | "画一只龙"                                                                                                                                                | "画一只龙"                         |
| 提示词 | `A majestic dragon, realistic fantasy art, cinematic composition, dramatic lighting, ultra-detailed, glowing runes on its scales, highly detailed 8K` | `A dragon for my D&D campaign` |
| 结果  | ❌ 脑补了风格/光影/细节                                                                                                                                         | ✅ 只说用户说的内容                     |

---

## 📌 本项目使用的模型

> 🔗 以下信息可供你在向 AI 助手描述配置需求时直接复制。

### 视觉识别模型

| 项目         | 内容                               |
| ---------- | -------------------------------- |
| **模型名**    | `nex-agi/Nex-N2-Pro`             |
| **提供方**    | SiliconFlow（硅基流动）                |
| **能力**     | 图片理解、OCR 文字识别、物体检测、场景描述、UI 分析    |
| **官网**     | https://www.siliconflow.cn/      |
| **API 类型** | OpenAI-compatible（兼容 OpenAI SDK） |

### 图片生成模型

| 项目      | 内容                      |
| ------- | ----------------------- |
| **模型名** | `agnes-image-2.1-flash` |
| **提供方** | Agnes AI                |
| **能力**  | 文生图、图生图（风格迁移）、高密度信息图片生成 |
| **官网**  | https://agnes-ai.com/   |
| **特点**  | 对提示词忠实度高，速度快，适合中文场景     |

---

## ❓ 常见问题

<details>
<summary><b>出现"❌ 识图未配置"错误</b></summary>

检查 `mcp-server/.env` 中 `SILICONFLOW_API_KEY` 是否已填写。确保：

1. `.env` 文件存在于 `mcp-server/` 目录下（不是 `.env.example`）

2. API Key 格式正确（以 `sk-` 开头）

3. API 账户余额充足

</details>

<details>
<summary><b>出现"❌ 生图未配置"错误</b></summary>

检查 `mcp-server/.env` 中 `AGNES_API_KEY` 是否已填写。该 Key 需要从对应服务商获取。

</details>

<details>
<summary><b>Claude Code 找不到 analyze_image / generate_image 工具</b></summary>

原因通常是 MCP Server 未正确注册。排查：

1. 确认 `~/.claude.json` 中的 `command` 路径指向正确的虚拟环境 Python

2. 单独在终端运行 `python mcp-server/server.py` 检查是否有报错

3. 重启 Claude Code 后重试

</details>

<details>
<summary><b>生成出来的图片跟描述不符</b></summary>

1. 确认提示词中没有拼写错误

2. 尝试增加关键细节（但不要脑补用户没说的内容）

3. 如果是中文提示词效果不佳，可以尝试英文提示词

4. 考虑更换生图模型

</details>

<details>
<summary><b>如何卸载？</b></summary>

1. 从 `~/.claude.json` 中移除 `image-mcp-server` 配置项

2. 删除 `~/.claude/skills/image-tools/` 目录

3. 删除项目文件夹

</details>

---

## 📄 许可

本项目基于 MIT 许可开源。

> **提示**：本项目不包含任何 API Key。请妥善保管你的 `.env` 文件，不要将其提交到版本控制系统。

---
