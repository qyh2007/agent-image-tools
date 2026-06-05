---
name: image-tools
description: Image handling constraints — use analyze_image for recognition, generate_image for generation, never Read for images
---

# Image Tools Usage Guide

## When to Use

**Must invoke this skill first** when the task involves:

- **Image recognition** — user provides an image (URL or local path), asks to describe content, recognize text, detect objects, etc.
- **Image generation** — user asks to generate an image
- **Image ambiguity** — user says "look at this image" without specifying what to do

## Tool Selection

### Recognition (Image Analysis)

**Two-step process: first verify existence, then analyze with MCP.**
- `Read` → only for checking file existence / resolving local path (just enough to confirm the file is reachable)
- `analyze_image` → the actual image understanding (description, OCR, object detection, scene analysis)

| User Action | My Response |
|-------------|-------------|
| Provides image URL | Call `analyze_image` with `image_path` set to the URL directly |
| Provides local path | (Optional) Use `Read` briefly to confirm the file exists, then call `analyze_image` with the path |
| Says "look at this image" with no path | Ask for the path/URL first, then call `analyze_image` |
| Drops image into VS Code chat | Use `Read` to resolve the local path (file existence check only), then call `analyze_image` for analysis |

### Generation (Image Creation)

| User Action | My Response |
|-------------|-------------|
| Text description for image | Call `generate_image` (returns URL by default, no download) |
| Reference image for style transfer | Call `generate_image` with `reference_image` parameter |

## Prohibited

- ❌ Do NOT use `Read` to "view" image files directly
- ❌ Do NOT say "I can't process images"
- ❌ Do NOT auto-download generated images to local disk

## Exception

Only fall back to `Read` for images when `image-mcp-server` is unavailable (MCP connection failed, tool not found).

## Prompt Construction Rule (CRITICAL)

Before calling `generate_image`, construct the prompt using the template below. **The template is for organizing what the user already told you — never invent elements the user did not mention.**

For example:
- User says: `a cat on a windowsill` → prompt: `A cat on a windowsill`
- User says: `a cat on a windowsill, cinematic lighting` → prompt: `A cat on a windowsill, cinematic lighting`
- ❌ Never turn `a cat on a windowsill` into `A cat sitting on a windowsill, cinematic realism, soft golden light, ultra-detailed` — that adds style, lighting, and quality the user never asked for.

### Text-to-Image Template

When the user provides any of these details, arrange them in this order:

```
[Subject] + [Scene / Environment] + [Style] + [Lighting] + [Composition] + [Quality Requirements]
```

**Only include fields the user mentioned. Skip the rest.**

| Element | When to include |
|---------|----------------|
| **Subject** | Always include — the core thing to depict |
| **Environment** | Only if user described the scene/background |
| **Style** | Only if user specified a style (e.g. "oil painting", "anime") |
| **Lighting** | Only if user specified lighting (e.g. "dim light", "sunset") |
| **Composition** | Only if user specified framing/angle |
| **Detail Level** | Only if user specified quality or detail |

### Image-to-Image Template

When editing an existing image, construct the prompt as:

```
[What to change] while preserving [what to keep]
```

**Only state what the user explicitly said to change or preserve.**

### High-Information-Density Images

Agnes Image 2.1 Flash is optimized for complex, detail-rich visuals. If the user's description naturally contains multiple elements, organize them clearly:

- **Subject** — focal point
- **Background** — scene atmosphere
- **Key secondary details** — supporting elements
- **Style & lighting** — overall visual direction
- **Composition constraints** — layout boundaries
- **(Image-to-image) What must stay unchanged**

Again: **only include what the user actually described.**

## Usage Examples

### Recognition

```
analyze_image(image_path="https://example.com/photo.jpg", prompt="Describe this image in detail")
```

### Text-to-Image

```
generate_image(prompt="A futuristic city marketplace filled with flying vehicles, holographic signs, dense crowds, neon lighting, cinematic realism, ultra-detailed, high-information-density composition", size="1024x768")
```

### Image-to-Image (Style Transfer)

```
generate_image(prompt="Transform the scene into a rain-soaked cyberpunk night with neon reflections while preserving the original composition and main subject layout.", reference_image="https://example.com/photo.jpg")
```
