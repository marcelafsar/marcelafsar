"""Turn a prepared portrait into a non-looping animated SVG ASCII portrait."""
from __future__ import annotations

import html
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "prepared-portrait.png"
SCENE = ROOT / "data" / "ascii_scene.txt"
OUTPUT = ROOT / "assets" / "marcel-ascii.svg"
PREVIEW = ROOT / "assets" / "marcel-ascii-preview.png"
STATIC = os.getenv("STATIC") == "1"
RAMP = "@%#*+=-:. "  # deliberately restrained: dense detail, then breathing room
COLS, ROWS, PAD = 48, 44, 7
WIDTH, HEIGHT = 430, 360


def portrait_crop(image: Image.Image) -> Image.Image:
    """Crop to a head-and-upper-body area with the face slightly above centre."""
    width, height = image.size
    wanted_ratio = COLS * 0.61 / ROWS
    crop_height = min(height, int(width / wanted_ratio))
    crop_width = int(crop_height * wanted_ratio)
    if crop_width > width:
        crop_width = width
        crop_height = int(crop_width / wanted_ratio)
    left = (width - crop_width) // 2
    top = max(0, min(height - crop_height, int(height * 0.06)))
    return image.crop((left, top, left + crop_width, top + crop_height))


def make_scene() -> list[str]:
    image = Image.open(SOURCE).convert("L")
    image = portrait_crop(image)
    image = ImageOps.fit(image, (COLS, ROWS), method=Image.Resampling.LANCZOS)
    pixels = list(image.get_flattened_data()) if hasattr(image, "get_flattened_data") else list(image.getdata())
    lines = []
    for row in range(ROWS):
        # Round instead of flooring so paper-white/background pixels become
        # actual spaces, not a distracting field of period glyphs.
        glyphs = "".join(RAMP[round(value * (len(RAMP) - 1) / 255)] for value in pixels[row * COLS:(row + 1) * COLS])
        lines.append(" " * PAD + glyphs.rstrip())
    return lines


def svg(lines: list[str]) -> str:
    cols = max(len(line) for line in lines)
    x0, y0 = 15, 42
    usable_width, usable_height = WIDTH - 30, HEIGHT - 58
    font_size = min(usable_width / (cols * 0.61), usable_height / len(lines))
    line_height = usable_height / len(lines)
    reveal_width = usable_width + 4
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="430" height="360" viewBox="0 0 430 360" role="img" aria-label="Animated photo-derived ASCII portrait of a developer">',
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1117"/><stop offset="1" stop-color="#090c10"/></linearGradient><filter id="glow"><feGaussianBlur stdDeviation="1.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>',
        '<rect x=".5" y=".5" width="429" height="359" rx="14" fill="url(#bg)" stroke="#30363d"/>',
        '<circle cx="18" cy="18" r="4" fill="#ff7b72"/><circle cx="32" cy="18" r="4" fill="#d29922"/><circle cx="46" cy="18" r="4" fill="#3fb950"/>',
        '<text x="62" y="22" fill="#8b949e" font-size="10.5" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">portrait.render()</text>',
        '<text x="362" y="22" fill="#58a6ff" font-size="10.5" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">ready</text><line x1="12" y1="31" x2="418" y2="31" stroke="#21262d"/>',
    ]
    for index, line in enumerate(lines):
        y = y0 + index * line_height
        clip_id = f"row-{index}"
        if STATIC:
            clip = f'<clipPath id="{clip_id}"><rect x="{x0}" y="{y-line_height+1:.2f}" width="{reveal_width:.2f}" height="{line_height+2:.2f}"/></clipPath>'
            cursor = ""
        else:
            begin = 0.08 + index * 0.060
            clip = f'<clipPath id="{clip_id}"><rect x="{x0}" y="{y-line_height+1:.2f}" width="0" height="{line_height+2:.2f}"><animate attributeName="width" from="0" to="{reveal_width:.2f}" dur="0.62s" begin="{begin:.3f}s" fill="freeze"/></rect></clipPath>'
            cursor = f'<rect x="{x0}" y="{y-line_height+1:.2f}" width="2.5" height="{line_height:.2f}" fill="#58a6ff" opacity="0" filter="url(#glow)"><animate attributeName="x" from="{x0}" to="{x0+reveal_width-2.5:.2f}" dur="0.62s" begin="{begin:.3f}s" fill="freeze"/><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.06;.88;1" dur="0.62s" begin="{begin:.3f}s" fill="freeze"/></rect>'
        parts.append(clip)
        parts.append(f'<text x="{x0}" y="{y:.2f}" xml:space="preserve" clip-path="url(#{clip_id})" fill="#c9d1d9" font-size="{font_size:.3f}" font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">{html.escape(line, quote=False)}</text>{cursor}')
    return "".join(parts) + "</svg>"


def png_preview(lines: list[str]) -> None:
    scale = 2
    canvas = Image.new("RGB", (WIDTH * scale, HEIGHT * scale), "#0d1117")
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((1, 1, WIDTH * scale - 2, HEIGHT * scale - 2), radius=14 * scale, outline="#30363d", width=scale)
    font_path = "C:/Windows/Fonts/consola.ttf"
    font = ImageFont.truetype(font_path, 10 * scale)
    small = ImageFont.truetype(font_path, 10 * scale)
    for x, color in ((18, "#ff7b72"), (32, "#d29922"), (46, "#3fb950")):
        draw.ellipse(((x-4)*scale, 14*scale, (x+4)*scale, 22*scale), fill=color)
    draw.text((62*scale, 12*scale), "portrait.render()", fill="#8b949e", font=small)
    draw.text((362*scale, 12*scale), "ready", fill="#58a6ff", font=small)
    draw.line((12*scale, 31*scale, 418*scale, 31*scale), fill="#21262d", width=scale)
    line_height = (HEIGHT - 58) / len(lines)
    for index, line in enumerate(lines):
        draw.text((15*scale, (42 + index * line_height - 9)*scale), line, fill="#c9d1d9", font=font)
    canvas.save(PREVIEW)


def build() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Missing {SOURCE}. Run scripts/prepare_portrait.py first.")
    lines = make_scene()
    SCENE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    OUTPUT.write_text(svg(lines), encoding="utf-8")
    png_preview(lines)
    print(f"Wrote {OUTPUT} and {PREVIEW}")


if __name__ == "__main__":
    build()
