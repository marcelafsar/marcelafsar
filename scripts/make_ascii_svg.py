from __future__ import annotations

import html
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "ascii_scene.txt"
OUTPUT = ROOT / "assets" / "marcel-ascii.svg"
STATIC = os.getenv("STATIC") == "1"


def build() -> None:
    raw_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    while raw_lines and not raw_lines[0].strip():
        raw_lines.pop(0)
    while raw_lines and not raw_lines[-1].strip():
        raw_lines.pop()

    cols = max(len(line) for line in raw_lines)
    rows = len(raw_lines)
    width, height = 430, 360
    x0, y0 = 15, 42
    usable_width = width - 30
    usable_height = height - 58
    font_size = min(usable_width / (cols * 0.61), usable_height / rows)
    line_height = usable_height / rows
    reveal_width = usable_width + 4

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="430" height="360" viewBox="0 0 430 360" role="img" aria-label="Animated ASCII developer coding at a workstation">',
        '<defs>',
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1117"/><stop offset="1" stop-color="#090c10"/></linearGradient>',
        '<filter id="glow"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '</defs>',
        '<rect x="0.5" y="0.5" width="429" height="359" rx="14" fill="url(#bg)" stroke="#30363d"/>',
        '<circle cx="18" cy="18" r="4" fill="#ff7b72"/><circle cx="32" cy="18" r="4" fill="#d29922"/><circle cx="46" cy="18" r="4" fill="#3fb950"/>',
        '<text x="62" y="22" fill="#8b949e" font-size="10.5" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">marcel@github:~/workspace</text>',
        '<text x="360" y="22" fill="#58a6ff" font-size="10.5" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">python main.py</text>',
        '<line x1="12" y1="31" x2="418" y2="31" stroke="#21262d"/>',
    ]

    for idx, line in enumerate(raw_lines):
        y = y0 + idx * line_height
        escaped = html.escape(line, quote=False)
        clip_id = f"row-{idx}"
        if STATIC:
            clip = f'<clipPath id="{clip_id}"><rect x="{x0}" y="{y-line_height+1:.2f}" width="{reveal_width:.2f}" height="{line_height+2:.2f}"/></clipPath>'
            cursor = ''
        else:
            begin = 0.07 + idx * 0.052
            clip = (
                f'<clipPath id="{clip_id}"><rect x="{x0}" y="{y-line_height+1:.2f}" width="0" height="{line_height+2:.2f}">'
                f'<animate attributeName="width" from="0" to="{reveal_width:.2f}" dur="0.72s" begin="{begin:.3f}s" fill="freeze"/>'
                '</rect></clipPath>'
            )
            cursor = (
                f'<rect x="{x0}" y="{y-line_height+1:.2f}" width="3" height="{line_height:.2f}" fill="#58a6ff" opacity="0" filter="url(#glow)">'
                f'<animate attributeName="x" from="{x0}" to="{x0+reveal_width-3:.2f}" dur="0.72s" begin="{begin:.3f}s" fill="freeze"/>'
                f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.05;0.88;1" dur="0.72s" begin="{begin:.3f}s" fill="freeze"/>'
                '</rect>'
            )
        parts.append(clip)
        parts.append(
            f'<text x="{x0}" y="{y:.2f}" xml:space="preserve" clip-path="url(#{clip_id})" '
            f'fill="#c9d1d9" font-size="{font_size:.3f}" font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">{escaped}</text>'
        )
        if cursor:
            parts.append(cursor)

    parts.append('</svg>')
    OUTPUT.write_text(''.join(parts), encoding='utf-8')
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build()
