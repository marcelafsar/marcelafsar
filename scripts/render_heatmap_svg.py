from __future__ import annotations

import html
import json
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "contributions.json"
OUTPUT = ROOT / "assets" / "contrib-heatmap.svg"
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


def sunday_index(d: date) -> int:
    return (d.weekday() + 1) % 7


def build() -> None:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    data_map = {item["date"]: item for item in payload.get("days", [])}
    stats = payload.get("stats", {})
    placeholder = not bool(data_map)

    today = date.today()
    current_sunday = today - timedelta(days=sunday_index(today))
    start = current_sunday - timedelta(weeks=52)

    width, height = 1000, 260
    x0, y0 = 58, 70
    cell, gap, step = 13, 4, 17

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="260" viewBox="0 0 1000 260" role="img" aria-label="GitHub contribution heatmap refreshed daily">',
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1117"/><stop offset="1" stop-color="#090c10"/></linearGradient></defs>',
        '<rect x="0.5" y="0.5" width="999" height="259" rx="14" fill="url(#bg)" stroke="#30363d"/>',
        '<text x="24" y="30" fill="#58a6ff" font-size="16" font-weight="700" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">› github activity</text>',
        '<text x="976" y="30" text-anchor="end" fill="#8b949e" font-size="11" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">auto-refreshed daily</text>',
    ]

    # Month labels at the column that contains each month's first day.
    shown = set()
    for col in range(53):
        week_start = start + timedelta(weeks=col)
        for offset in range(7):
            d = week_start + timedelta(days=offset)
            if d.day == 1 and d.month not in shown:
                parts.append(
                    f'<text x="{x0 + col*step}" y="54" fill="#8b949e" font-size="10.5" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">{d.strftime("%b")}</text>'
                )
                shown.add(d.month)
                break

    for label, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
        parts.append(f'<text x="18" y="{y0 + row*step + 10}" fill="#8b949e" font-size="10" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">{label}</text>')

    for col in range(53):
        for row in range(7):
            d = start + timedelta(weeks=col, days=row)
            if d > today:
                continue
            item = data_map.get(d.isoformat(), {"count": 0, "level": 0})
            level = max(0, min(4, int(item.get("level", 0))))
            count = int(item.get("count", 0))
            x, y = x0 + col*step, y0 + row*step
            begin = 0.02 * (col + row) + 0.08
            title = html.escape(f"{d.isoformat()}: {count} contribution{'s' if count != 1 else ''}")
            parts.append(
                f'<g opacity="0" transform="translate(0 -8)">'
                f'<title>{title}</title>'
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{PALETTE[level]}"/>'
                f'<animate attributeName="opacity" from="0" to="1" dur="0.32s" begin="{begin:.2f}s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" from="0 -8" to="0 0" dur="0.32s" begin="{begin:.2f}s" fill="freeze"/>'
                '</g>'
            )

    footer_y = 226
    if placeholder:
        footer = "Run the GitHub Action once to load live contribution data"
    else:
        total = int(stats.get("total", 0))
        current = int(stats.get("current_streak", 0))
        longest = int(stats.get("longest_streak", 0))
        best = stats.get("best_day", {}) or {}
        best_count = int(best.get("count", 0) or 0)
        footer = f"{total} contributions · current streak {current}d · longest {longest}d · best day {best_count}"
    parts.append(f'<text x="24" y="{footer_y}" fill="#c9d1d9" font-size="12" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">{html.escape(footer)}</text>')

    legend_x = 790
    parts.append(f'<text x="{legend_x-35}" y="{footer_y}" fill="#8b949e" font-size="10" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">Less</text>')
    for i, color in enumerate(PALETTE):
        parts.append(f'<rect x="{legend_x + i*19}" y="{footer_y-11}" width="13" height="13" rx="3" fill="{color}"/>')
    parts.append(f'<text x="{legend_x+103}" y="{footer_y}" fill="#8b949e" font-size="10" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">More</text>')
    parts.append('</svg>')
    OUTPUT.write_text(''.join(parts), encoding='utf-8')
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build()
