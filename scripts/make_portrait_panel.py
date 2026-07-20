"""Render the GitHub-safe terminal frame around the regular portrait image."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "marcel-portrait.png"
OUTPUT = ROOT / "assets" / "marcel-portrait-panel.png"
WIDTH, HEIGHT, SCALE = 430, 360, 2


def build() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Missing {SOURCE}. Add your photo, then run this script.")
    canvas = Image.new("RGB", (WIDTH * SCALE, HEIGHT * SCALE), "#0d1117")
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((1, 1, WIDTH * SCALE - 2, HEIGHT * SCALE - 2), radius=14 * SCALE, outline="#30363d", width=SCALE)

    for x, colour in ((18, "#ff7b72"), (32, "#d29922"), (46, "#3fb950")):
        draw.ellipse(((x - 4) * SCALE, 14 * SCALE, (x + 4) * SCALE, 22 * SCALE), fill=colour)
    font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 10 * SCALE)
    draw.text((62 * SCALE, 12 * SCALE), "portrait.png", fill="#8b949e", font=font)
    draw.text((374 * SCALE, 12 * SCALE), "ready", fill="#58a6ff", font=font)
    draw.line((12 * SCALE, 31 * SCALE, 418 * SCALE, 31 * SCALE), fill="#21262d", width=SCALE)

    # Crop instead of stretching: the photo fills the content well while its
    # central head-and-shoulders composition remains centred.
    portrait = Image.open(SOURCE).convert("RGB")
    content_box = (12 * SCALE, 42 * SCALE, 418 * SCALE, 348 * SCALE)
    target_size = (content_box[2] - content_box[0], content_box[3] - content_box[1])
    portrait = ImageOps.fit(portrait, target_size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.36))
    mask = Image.new("L", target_size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, target_size[0] - 1, target_size[1] - 1), radius=8 * SCALE, fill=255)
    canvas.paste(portrait, content_box[:2], mask)
    canvas.save(OUTPUT, optimize=True)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build()
