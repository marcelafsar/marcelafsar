from __future__ import annotations

import html
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "info-card.svg"
STATIC = os.getenv("STATIC") == "1"

ROWS = [
    ("Role", "Student Software Developer"),
    ("Focus", "Python · Full-Stack · AI Applications"),
    ("Strong", "Python · AI APIs · Computer Vision"),
    ("Web", "HTML · CSS · JavaScript · React"),
    ("Backend", "FastAPI · SQLite · Git"),
    ("Desktop", "PyQt6 · Electron"),
    ("Building", "Zovryn AI · Location Simulator"),
    ("Learning", "C++"),
    ("Open to", "Internships · Collaboration · Freelance"),
]


def animated_group(content: str, idx: int) -> str:
    if STATIC:
        return f'<g opacity="1">{content}</g>'
    begin = 0.18 + idx * 0.14
    return (
        '<g opacity="0" transform="translate(12 0)">'
        f'<animate attributeName="opacity" from="0" to="1" dur="0.34s" begin="{begin:.2f}s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" from="12 0" to="0 0" dur="0.34s" begin="{begin:.2f}s" fill="freeze"/>'
        f'{content}</g>'
    )


def build() -> None:
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="570" height="360" viewBox="0 0 570 360" role="img" aria-label="Marcel Afsar developer information card">',
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1117"/><stop offset="1" stop-color="#090c10"/></linearGradient></defs>',
        '<rect x="0.5" y="0.5" width="569" height="359" rx="14" fill="url(#bg)" stroke="#30363d"/>',
        '<circle cx="18" cy="18" r="4" fill="#ff7b72"/><circle cx="32" cy="18" r="4" fill="#d29922"/><circle cx="46" cy="18" r="4" fill="#3fb950"/>',
        '<text x="62" y="22" fill="#8b949e" font-size="10.5" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">neofetch --profile marcel</text>',
        '<line x1="12" y1="31" x2="558" y2="31" stroke="#21262d"/>',
    ]

    title = (
        '<text x="25" y="64" fill="#58a6ff" font-size="19" font-weight="700" '
        'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">› marcel@github</text>'
    )
    parts.append(animated_group(title, 0))

    start_y, step = 96, 26
    for idx, (key, value) in enumerate(ROWS, start=1):
        y = start_y + (idx-1) * step
        row = (
            f'<text x="28" y="{y}" fill="#58a6ff" font-size="14.5" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">{html.escape(key)}</text>'
            f'<text x="137" y="{y}" fill="#c9d1d9" font-size="14.5" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">{html.escape(value)}</text>'
        )
        parts.append(animated_group(row, idx))

    parts.extend([
        '<line x1="25" y1="333" x2="545" y2="333" stroke="#21262d"/>',
        '<text x="28" y="350" fill="#8b949e" font-size="10.8" font-style="italic" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">Building desktop applications, full-stack tools, and AI-powered software.</text>',
        '</svg>',
    ])
    OUTPUT.write_text(''.join(parts), encoding='utf-8')
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build()
