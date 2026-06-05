#!/usr/bin/env python3
"""Generate a short English promo video for cursor-mem0 (no API key required)."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs"
OUT_VIDEO = OUT_DIR / "demo.mp4"

W, H = 1280, 720
FPS = 30

# Palette — Cursor-ish dark UI
BG = (15, 17, 23)
PANEL = (22, 25, 32)
PANEL_BORDER = (42, 46, 58)
FG = (230, 233, 240)
ACCENT = (78, 156, 255)
MUTED = (140, 148, 163)
GREEN = (72, 199, 142)
RED = (255, 110, 110)
USER_BUBBLE = (35, 48, 72)
AI_BUBBLE = (28, 31, 40)
TOOL_BG = (18, 38, 32)
TOOL_BORDER = (46, 120, 90)
MONO = (180, 220, 180)


def load_font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if mono:
        candidates = [
            "/System/Library/Fonts/Menlo.ttc",
            "/System/Library/Fonts/Supplemental/Courier New.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        ]
    elif bold:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img)


def footer(draw: ImageDraw.ImageDraw, text: str = "github.com/xwqiang/cursor-mem0") -> None:
    draw.text((48, H - 44), text, font=load_font(20), fill=MUTED)


def scene_banner(draw: ImageDraw.ImageDraw, title: str, subtitle: str, color: tuple[int, int, int]) -> None:
    draw.rectangle((0, 0, W, 5), fill=color)
    draw.text((48, 28), title, font=load_font(36, bold=True), fill=color)
    draw.text((48, 78), subtitle, font=load_font(22), fill=MUTED)


def rounded_rect(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    fill: tuple[int, int, int],
    outline: tuple[int, int, int] | None = None,
    radius: int = 12,
) -> None:
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=1 if outline else 0)


def render_title_slide() -> Image.Image:
    img, draw = canvas()
    draw.rectangle((0, 0, W, 6), fill=ACCENT)
    draw.text((64, 200), "cursor-mem0", font=load_font(72, bold=True), fill=FG)
    draw.text((64, 300), "Long-term memory for Cursor agents", font=load_font(34), fill=FG)
    draw.text((64, 360), "mem0 pipeline  ·  one API key  ·  MCP ready", font=load_font(28), fill=MUTED)
    draw.text((64, 460), "pip install \"cursor-mem0[mcp]\"", font=load_font(26, mono=True), fill=GREEN)
    footer(draw)
    return img


def render_problem_slide(kind: str) -> Image.Image:
    img, draw = canvas()
    if kind == "keys":
        scene_banner(draw, "The problem", "Extra API keys on top of Cursor", RED)
        lines = [
            "mem0 default  →  OPENAI_API_KEY for extraction",
            "Many tools    →  + Anthropic / embedding APIs",
            "Result        →  second bill, second key rotation",
        ]
    else:
        scene_banner(draw, "The problem", "File-based memory wastes tokens", RED)
        lines = [
            "MEMORY.md grows to 50+ facts over weeks",
            "Agent loads the whole file every new chat",
            "Context cost scales with memory size — not with relevance",
        ]
    y = 160
    rounded_rect(draw, (48, 130, W - 48, 520), PANEL, PANEL_BORDER)
    for line in lines:
        draw.text((80, y), line, font=load_font(28, mono=True), fill=FG)
        y += 56
    footer(draw)
    return img


def render_cursor_window(
    scene_title: str,
    scene_sub: str,
    messages: list[tuple[str, str]],
    mcp_sidebar: list[str] | None = None,
    highlight_last: bool = False,
) -> Image.Image:
    """Mock Cursor chat with optional MCP tool sidebar."""
    img, draw = canvas()
    scene_banner(draw, scene_title, scene_sub, ACCENT)

    chat_w = W - 360 if mcp_sidebar else W - 96
    rounded_rect(draw, (48, 120, chat_w, H - 60), PANEL, PANEL_BORDER)

    # Window chrome
    draw.text((68, 136), "Cursor  ·  Chat", font=load_font(18), fill=MUTED)
    draw.line((68, 162, chat_w - 20, 162), fill=PANEL_BORDER, width=1)

    y = 180
    for role, text in messages:
        is_user = role == "user"
        color = USER_BUBBLE if is_user else AI_BUBBLE
        label = "You" if is_user else "Agent"
        label_color = ACCENT if is_user else GREEN
        rounded_rect(draw, (72, y, chat_w - 32, y + 88), color, PANEL_BORDER, radius=10)
        draw.text((88, y + 12), label, font=load_font(16, bold=True), fill=label_color)
        draw.text((88, y + 36), text, font=load_font(20), fill=FG)
        y += 104

    if highlight_last and messages:
        x0, y0 = 64, y - 104
        draw.rounded_rectangle((x0, y0, chat_w - 24, y0 + 88), radius=12, outline=GREEN, width=2)

    if mcp_sidebar:
        sx0 = chat_w + 16
        rounded_rect(draw, (sx0, 120, W - 48, H - 60), TOOL_BG, TOOL_BORDER)
        draw.text((sx0 + 16, 136), "MCP · cursor-mem", font=load_font(18, bold=True), fill=GREEN)
        draw.line((sx0 + 16, 162, W - 64, 162), fill=TOOL_BORDER, width=1)
        ty = 180
        for item in mcp_sidebar:
            for i, line in enumerate(item.split("\n")):
                font = load_font(17, bold=True) if i == 0 else load_font(15, mono=True)
                fill = GREEN if i == 0 else MONO
                draw.text((sx0 + 16, ty), line, font=font, fill=fill)
                ty += 22
            ty += 14

    footer(draw)
    return img


def render_without_memory() -> Image.Image:
    return render_cursor_window(
        "Without cursor-mem",
        "New chat — the agent has no memory of past sessions",
        [
            ("user", "What theme and keybindings do I prefer?"),
            ("agent", "I don't have information about your preferences yet."),
        ],
        highlight_last=True,
    )


def render_add_memory_session() -> Image.Image:
    return render_cursor_window(
        "With cursor-mem — Session 1",
        "User shares preferences · Agent stores structured facts via MCP",
        [
            ("user", "Remember: I prefer dark mode and vim keybindings."),
            ("agent", "Got it — I'll save that to long-term memory."),
        ],
        mcp_sidebar=[
            "▶ add_memory\n  infer: true\n  user_id: alice\n\n  stored:\n  · Prefers dark mode\n  · Uses vim keybindings",
        ],
    )


def render_search_memory_session() -> Image.Image:
    return render_cursor_window(
        "With cursor-mem — Session 2",
        "Brand-new chat · search_memories returns only relevant facts",
        [
            ("user", "Set up my editor the way I like."),
            ("agent", "Dark mode + vim keybindings — as you prefer."),
        ],
        mcp_sidebar=[
            "▶ search_memories\n  query: editor setup\n  top_k: 3\n\n  hits:\n  · Prefers dark mode (0.92)\n  · Uses vim keybindings (0.89)",
        ],
        highlight_last=True,
    )


def render_token_comparison() -> Image.Image:
    img, draw = canvas()
    scene_banner(draw, "Retrieve, don't dump", "Only top_k memories enter the prompt", GREEN)

    rounded_rect(draw, (48, 130, 610, 520), (40, 28, 28), RED)
    draw.text((72, 150), "File-based memory", font=load_font(24, bold=True), fill=RED)
    for i, line in enumerate(
        [
            "Load entire MEMORY.md each turn",
            "~50 facts → ~3,000+ tokens",
            "Noise grows with every new note",
        ]
    ):
        draw.text((72, 210 + i * 44), line, font=load_font(22), fill=FG)

    rounded_rect(draw, (660, 130, W - 48, 520), TOOL_BG, GREEN)
    draw.text((684, 150), "cursor-mem0", font=load_font(24, bold=True), fill=GREEN)
    for i, line in enumerate(
        [
            "search_memories(query, top_k=3)",
            "~3 facts → ~300 tokens",
            "Cost stays bounded as store grows",
        ]
    ):
        draw.text((684, 210 + i * 44), line, font=load_font(22), fill=FG)

    draw.text((48, 540), "Structured extraction  →  Qdrant + BM25 + entities", font=load_font(22), fill=MUTED)
    footer(draw)
    return img


def render_mcp_setup() -> Image.Image:
    img, draw = canvas()
    scene_banner(draw, "MCP in Cursor", "Enable once — memory tools in every project", ACCENT)

    rounded_rect(draw, (48, 130, W - 48, 400), PANEL, PANEL_BORDER)
    config = '''{
  "mcpServers": {
    "cursor-mem": {
      "command": "python3",
      "args": ["-m", "cursor_mem.mcp_server"]
    }
  }
}'''
    draw.text((72, 150), ".cursor/mcp.json", font=load_font(22, bold=True), fill=ACCENT)
    y = 190
    for line in config.split("\n"):
        draw.text((88, y), line, font=load_font(20, mono=True), fill=MONO)
        y += 30

    tools = "add_memory  ·  search_memories  ·  list_memories  ·  get_memory"
    draw.text((72, 430), tools, font=load_font(22), fill=GREEN)
    draw.text((72, 470), "Only CURSOR_API_KEY required — embeddings run locally (fastembed)", font=load_font(20), fill=MUTED)
    footer(draw)
    return img


def render_get_started() -> Image.Image:
    img, draw = canvas()
    draw.rectangle((0, 0, W, 6), fill=ACCENT)
    draw.text((64, 180), "Get started", font=load_font(56, bold=True), fill=FG)
    steps = [
        "pip install \"cursor-mem0[mcp]\"",
        "export CURSOR_API_KEY=\"cursor_...\"",
        "Enable cursor-mem in Cursor → MCP",
        "Agents remember across sessions",
    ]
    y = 280
    for i, step in enumerate(steps, 1):
        draw.text((64, y), f"{i}.", font=load_font(28, bold=True), fill=ACCENT)
        draw.text((110, y), step, font=load_font(26, mono=True), fill=FG if i < 4 else GREEN)
        y += 56
    draw.text((64, 520), "https://github.com/xwqiang/cursor-mem0", font=load_font(24), fill=ACCENT)
    footer(draw)
    return img


# (renderer, duration_seconds)
SCENES: list[tuple[Callable[[], Image.Image], float]] = [
    (render_title_slide, 4.0),
    (lambda: render_problem_slide("keys"), 4.5),
    (lambda: render_problem_slide("files"), 4.5),
    (render_without_memory, 6.0),
    (render_add_memory_session, 7.0),
    (render_search_memory_session, 7.0),
    (render_token_comparison, 5.0),
    (render_mcp_setup, 6.0),
    (render_get_started, 5.0),
]


def write_video(frame_paths: list[Path], output: Path) -> None:
    list_file = output.parent / "frames.txt"
    with list_file.open("w") as f:
        for path in frame_paths:
            f.write(f"file '{path}'\n")
            f.write(f"duration {1 / FPS}\n")
        if frame_paths:
            f.write(f"file '{frame_paths[-1]}'\n")

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_file),
        "-vf",
        f"fps={FPS},scale={W}:{H},format=yuv420p",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(output),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    list_file.unlink(missing_ok=True)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total_sec = sum(d for _, d in SCENES)

    with tempfile.TemporaryDirectory(prefix="cursor-mem-demo-") as tmp:
        tmp_path = Path(tmp)
        frame_paths: list[Path] = []
        frame_idx = 0

        for render, duration in SCENES:
            img = render()
            frames = max(1, int(duration * FPS))
            for _ in range(frames):
                path = tmp_path / f"frame_{frame_idx:06d}.png"
                img.save(path)
                frame_paths.append(path)
                frame_idx += 1

        write_video(frame_paths, OUT_VIDEO)

    print(f"Wrote {OUT_VIDEO} ({len(SCENES)} scenes, ~{total_sec:.0f}s, {frame_idx} frames)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
