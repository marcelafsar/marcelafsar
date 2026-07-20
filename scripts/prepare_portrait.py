"""Prepare a portrait for the profile's photo-derived ASCII renderer.

The source can be a JPG, PNG, or WebP.  PNG transparency is preserved; for
ordinary photos, a conservative border flood-fill clears a flat studio-style
background without trying to cut through hair or clothing.
"""
from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "data" / "source" / "portrait-reference.png"
DEFAULT_OUTPUT = ROOT / "data" / "prepared-portrait.png"


def clear_flat_border_background(image: Image.Image, tolerance: int = 34) -> Image.Image:
    """Make pixels connected to a similarly coloured border transparent.

    This deliberately only handles simple, even backgrounds.  A real photo
    with a busy background remains intact rather than receiving a bad cutout.
    """
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size
    samples = [pixels[x, y][:3] for x, y in ((0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1))]
    reference = tuple(sum(channel) // len(samples) for channel in zip(*samples))

    def close_to_background(x: int, y: int) -> bool:
        red, green, blue, alpha = pixels[x, y]
        return alpha and sum((value - base) ** 2 for value, base in zip((red, green, blue), reference)) ** 0.5 <= tolerance

    queue = deque()
    visited: set[tuple[int, int]] = set()
    for x in range(width):
        queue.extend(((x, 0), (x, height - 1)))
    for y in range(height):
        queue.extend(((0, y), (width - 1, y)))
    while queue:
        x, y = queue.popleft()
        if (x, y) in visited or not (0 <= x < width and 0 <= y < height) or not close_to_background(x, y):
            continue
        visited.add((x, y))
        red, green, blue, _ = pixels[x, y]
        pixels[x, y] = (red, green, blue, 0)
        queue.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return rgba


def prepare(source: Path, output: Path) -> None:
    image = Image.open(source).convert("RGBA")
    if image.getextrema()[3][0] == 255:
        image = clear_flat_border_background(image)
    # A white base makes transparent/cleared regions render as empty ASCII.
    base = Image.new("RGBA", image.size, (255, 255, 255, 255))
    base.alpha_composite(image)
    gray = ImageOps.grayscale(base)
    gray = ImageOps.autocontrast(gray, cutoff=1)
    gray = ImageEnhance.Contrast(gray).enhance(1.22)
    gray = gray.filter(ImageFilter.UnsharpMask(radius=1.1, percent=125, threshold=3))
    output.parent.mkdir(parents=True, exist_ok=True)
    gray.save(output)
    print(f"Prepared {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare a reference photo for ASCII conversion.")
    parser.add_argument("source", nargs="?", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    prepare(args.source, args.output)
