"""
Image MCP Server — 图片理解 + 生成

遵循 MCP 最佳实践 (FastMCP):
  • analyze_image   — 识图 (via SiliconFlow OpenAI-compatible API)
  • generate_image  — 文生图 / 图生图 (via Agnes AI)

.env 需配置:
  SILICONFLOW_API_KEY=sk-...    (硅基流动, 识图)
  AGNES_API_KEY=sk-...          (Agnes AI, 生图)
"""

import os
import base64
import json
import uuid
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict

# ── 加载 .env ──────────────────────────────────────────────────
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

# ── 识图: 硅基流动 ──────────────────────────────────────────
VISION_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
VISION_BASE_URL = os.getenv("VISION_BASE_URL", "https://api.siliconflow.cn/v1")
VISION_MODEL = os.getenv("VISION_MODEL", "nex-agi/Nex-N2-Pro")

# ── 生图: Agnes AI ─────────────────────────────────────────
GEN_API_KEY = os.getenv("AGNES_API_KEY", "")
GEN_BASE_URL = os.getenv("AGNES_BASE_URL", "https://apihub.agnes-ai.com/v1")
GEN_MODEL = os.getenv("GENERATION_MODEL", "agnes-image-2.1-flash")

# ── 保存路径（可选）─────────────────────────────────────────
IMAGE_SAVE_DIR = os.getenv("IMAGE_SAVE_DIR", "")

# ── MCP 服务器 ─────────────────────────────────────────────
mcp = FastMCP("image_mcp")


# ════════════════════════════════════════════════════════════════
# Pydantic 输入模型
# ════════════════════════════════════════════════════════════════

class AnalyzeImageInput(BaseModel):
    """分析图片的输入参数."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    image_path: str = Field(
        ...,
        description="图片路径 (本地绝对路径或 http/https URL)",
        min_length=1,
    )
    prompt: str = Field(
        default="请详细描述这张图片的内容，包括物体、文字、颜色、布局等",
        description="对图片提出的具体问题或描述要求",
    )
    model: Optional[str] = Field(
        default=None,
        description="视觉模型名称 (留空则使用环境变量 VISION_MODEL)",
    )
    max_tokens: int = Field(
        default=2048,
        description="最大输出 Token 数",
        ge=64,
        le=8192,
    )


class GenerateImageInput(BaseModel):
    """生成图片的输入参数."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    prompt: str = Field(
        ...,
        description="图片描述提示词",
        min_length=1,
        max_length=2000,
    )
    size: str = Field(
        default="1024x768",
        description="图片尺寸 (格式: 宽x高, 如 1024x768)",
        pattern=r"^\d+x\d+$",
    )
    reference_image: Optional[str] = Field(
        default=None,
        description="参考图 URL (用于图生图风格转换)",
    )
    response_format: str = Field(
        default="url",
        description="返回格式: 'url' 或 'b64_json'",
    )


# ════════════════════════════════════════════════════════════════
# 共享工具函数
# ════════════════════════════════════════════════════════════════

def _encode_image(image_path: str) -> str:
    """将图片文件或 URL 编码为 data URI (base64).

    优先使用 httpx, 降级到 urllib (兼容 Windows TLS 环境).
    """
    if image_path.startswith(("http://", "https://")):
        try:
            import httpx
            resp = httpx.get(image_path, timeout=60)
            resp.raise_for_status()
            content_type = resp.headers.get("content-type", "image/png")
            b64 = base64.b64encode(resp.content).decode("utf-8")
            return f"data:{content_type};base64,{b64}"
        except Exception:
            # Fallback: urllib (更稳定的 Windows TLS)
            import urllib.request
            with urllib.request.urlopen(image_path, timeout=60) as r:
                data = r.read()
                content_type = r.headers.get_content_type() or "image/png"
                b64 = base64.b64encode(data).decode("utf-8")
                return f"data:{content_type};base64,{b64}"

    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"图片文件不存在: {image_path}")

    suffix = path.suffix.lower().lstrip(".")
    mime_map = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
        "gif": "image/gif",
        "bmp": "image/bmp",
    }
    mime = mime_map.get(suffix, "image/png")

    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


async def _vision_request(
    image_data_url: str,
    prompt: str,
    model: str,
    max_tokens: int,
) -> dict:
    """向视觉 API 发起聊天补全请求."""
    import httpx

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                    {"type": "text", "text": prompt},
                ],
            }
        ],
        "max_tokens": max_tokens,
    }

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{VISION_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {VISION_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()


async def _generation_request(payload: dict) -> dict:
    """向生图 API 发起图片生成请求."""
    import httpx

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{GEN_BASE_URL}/images/generations",
            headers={
                "Authorization": f"Bearer {GEN_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()


def _handle_api_error(e: Exception, context: str = "API") -> str:
    """统一的错误格式化, 提供可操作的错误消息."""
    import httpx

    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        detail = e.response.text[:2000]
        if status == 401:
            return (
                f"❌ {context} 认证失败 (HTTP 401)\n"
                f"请检查 API Key 是否正确\n"
                f"详情: {detail}"
            )
        if status == 403:
            return (
                f"❌ {context} 权限不足 (HTTP 403)\n"
                f"请检查 API Key 是否有权限访问该模型\n"
                f"详情: {detail}"
            )
        if status == 429:
            return (
                f"❌ {context} 请求过于频繁 (HTTP 429)\n"
                f"请稍后重试"
            )
        return f"❌ {context} 请求失败 (HTTP {status}):\n{detail}"
    if isinstance(e, httpx.TimeoutException):
        return f"❌ {context} 请求超时, 请重试"
    if isinstance(e, FileNotFoundError):
        return f"❌ {e}"
    return f"❌ {context} 异常 ({type(e).__name__}): {e}"


# ════════════════════════════════════════════════════════════════
# Tool: analyze_image — 识图
# ════════════════════════════════════════════════════════════════
@mcp.tool(
    name="analyze_image",
    annotations={
        "title": "分析图片内容",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def analyze_image(params: AnalyzeImageInput) -> str:
    """分析一张图片的内容, 支持 OCR 识别、物体检测、场景描述、布局分析、UI 审查等。

    通过 SiliconFlow 的视觉语言模型处理图片, 可以识别图片中的文字、物体、
    颜色、布局等信息。支持本地图片路径和网络图片 URL。

    Args:
        params (AnalyzeImageInput): 输入参数包含:
            - image_path (str): 图片路径 (本地绝对路径或 http/https URL)
            - prompt (str): 对图片提出的具体问题或描述要求 (默认: 通用描述)
            - model (Optional[str]): 视觉模型名称, 留空使用 VISION_MODEL
            - max_tokens (int): 最大输出 Token 数 (默认: 2048)

    Returns:
        str: 图片分析结果文本, 包含模型回答和使用统计

    Examples:
        - 使用场景: OCR 识别 → prompt = "提取图中所有文字"
        - 使用场景: UI 分析 → prompt = "分析这个界面布局和交互元素"
        - 使用场景: 物体检测 → prompt = "图中有什么物体? 分别在什么位置?"

    Error Handling:
        - API Key 未配置 → 提示用户配置 SILICONFLOW_API_KEY
        - 文件不存在 → 提示检查路径
        - 认证失败 (401) → 提示检查 API Key
        - 模型无权限 (403) → 提示检查模型权限
    """
    if not VISION_API_KEY:
        return (
            "❌ 识图未配置\n"
            "请在 .env 中设置 SILICONFLOW_API_KEY\n"
            "免费注册: https://cloud.siliconflow.cn/ → API 密钥"
        )

    model_name = params.model or VISION_MODEL

    try:
        image_data_url = _encode_image(params.image_path)

        data = await _vision_request(
            image_data_url=image_data_url,
            prompt=params.prompt,
            model=model_name,
            max_tokens=params.max_tokens,
        )

        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})

        detail = (
            f"（模型: {model_name}, "
            f"输入: {usage.get('prompt_tokens', '?')} tokens, "
            f"输出: {usage.get('completion_tokens', '?')} tokens）"
        )
        return f"{content}\n\n---\n{detail}"

    except Exception as e:
        return _handle_api_error(e, "识图")


# ════════════════════════════════════════════════════════════════
# Tool: generate_image — 生图
# ════════════════════════════════════════════════════════════════
@mcp.tool(
    name="generate_image",
    annotations={
        "title": "生成图片",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def generate_image(params: GenerateImageInput) -> str:
    """根据文字描述生成图片, 或基于参考图进行风格转换 (图生图)。

    通过 Agnes AI 的 agnes-image-2.1-flash 模型生成高质量图片。
    支持纯文本生图和参考图风格迁移。

    Args:
        params (GenerateImageInput): 输入参数包含:
            - prompt (str): 图片描述提示词 (必填)
            - size (str): 图片尺寸, 格式如 1024x768 (默认: 1024x768)
            - reference_image (Optional[str]): 参考图 URL, 用于风格转换
            - response_format (str): 返回格式 'url' 或 'b64_json' (默认: 'url')

    Returns:
        str: 生成的图片 URL 或本地保存路径

    Examples:
        - 使用场景: 文生图 → prompt = "一只可爱的橘猫坐在窗台上, 阳光洒进来"
        - 使用场景: 风格转换 → prompt + reference_image

    Error Handling:
        - API Key 未配置 → 提示用户配置 AGNES_API_KEY
        - 认证失败 (401) → 提示检查 API Key
    """
    if not GEN_API_KEY:
        return (
            "❌ 生图未配置\n"
            "请在 .env 中设置 AGNES_API_KEY\n"
            "获取: https://apihub.agnes-ai.com → API 密钥"
        )

    try:
        payload: dict = {
            "model": GEN_MODEL,
            "prompt": params.prompt,
            "size": params.size,
        }

        if params.reference_image:
            payload["extra_body"] = {
                "image": [params.reference_image],
                "response_format": params.response_format,
            }

        data = await _generation_request(payload)
        image_url = data["data"][0]["url"]

        if IMAGE_SAVE_DIR:
            return await _download_image(image_url)

        return f"✅ 生成成功！图片 URL:\n{image_url}"

    except (KeyError, IndexError) as e:
        return (
            f"❌ 生图返回数据异常: {e}\n"
            f"原始响应: {{...}}"
        )
    except Exception as e:
        return _handle_api_error(e, "生图")


# ════════════════════════════════════════════════════════════════
# 辅助: 下载图片到本地
# ════════════════════════════════════════════════════════════════
async def _download_image(image_url: str) -> str:
    """将生成的图片下载到本地保存目录."""
    import httpx

    save_dir = Path(IMAGE_SAVE_DIR)
    save_dir.mkdir(parents=True, exist_ok=True)

    filename = f"gen_{uuid.uuid4().hex[:12]}.png"
    save_path = save_dir / filename

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(image_url)
        resp.raise_for_status()
        save_path.write_bytes(resp.content)

    return f"✅ 生成成功！已保存至: {save_path}"


# ════════════════════════════════════════════════════════════════
# 入口
# ════════════════════════════════════════════════════════════════
def main():
    """以 stdio 模式启动 MCP 服务器."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
