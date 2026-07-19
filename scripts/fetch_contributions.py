from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "contributions.json"
USERNAME = "marcelafsar"
URL = f"https://github.com/users/{USERNAME}/contributions"


def parse_count(cell, soup: BeautifulSoup) -> int:
    for attr in ("data-count", "data-value"):
        value = cell.get(attr)
        if value is not None and str(value).isdigit():
            return int(value)

    label = cell.get("aria-label") or cell.get("title") or ""
    cell_id = cell.get("id")
    if not label and cell_id:
        tooltip = soup.find("tool-tip", attrs={"for": cell_id})
        if tooltip:
            label = tooltip.get_text(" ", strip=True)

    match = re.search(r"(\d+)\s+contribution", label, flags=re.I)
    return int(match.group(1)) if match else 0


def calculate_stats(days: list[dict]) -> dict:
    counts = {date.fromisoformat(item["date"]): int(item["count"]) for item in days}
    today = date.today()
    active_dates = sorted(d for d, count in counts.items() if count > 0 and d <= today)

    longest = 0
    run = 0
    previous = None
    for d in active_dates:
        if previous and d == previous + timedelta(days=1):
            run += 1
        else:
            run = 1
        longest = max(longest, run)
        previous = d

    current = 0
    cursor = today
    # A current streak can continue from yesterday when today has no activity yet.
    if counts.get(cursor, 0) == 0:
        cursor -= timedelta(days=1)
    while counts.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)

    best = max(days, key=lambda item: int(item["count"]), default={"date": None, "count": 0})
    monthly = defaultdict(int)
    for item in days:
        monthly[item["date"][:7]] += int(item["count"])

    return {
        "total": sum(int(item["count"]) for item in days),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
        "monthly_totals": dict(sorted(monthly.items())),
    }


def main() -> None:
    response = requests.get(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; marcelafsar-profile-readme/1.0)",
            "Accept": "text/html,application/xhtml+xml",
        },
        timeout=30,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    cells = soup.select("[data-date][data-level]")
    if not cells:
        cells = soup.select(".ContributionCalendar-day[data-date]")
    if not cells:
        raise RuntimeError("GitHub contribution cells were not found; the page structure may have changed.")

    by_date: dict[str, dict] = {}
    for cell in cells:
        day = cell.get("data-date")
        if not day:
            continue
        try:
            date.fromisoformat(day)
        except ValueError:
            continue
        level_raw = cell.get("data-level", 0)
        try:
            level = max(0, min(4, int(level_raw)))
        except (TypeError, ValueError):
            level = 0
        count = parse_count(cell, soup)
        previous = by_date.get(day)
        if previous is None or count > previous["count"]:
            by_date[day] = {"date": day, "count": count, "level": level}

    days = [by_date[key] for key in sorted(by_date)]
    if not days:
        raise RuntimeError("No valid contribution dates were parsed.")

    payload = {
        "username": USERNAME,
        "source": URL,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
        "stats": calculate_stats(days),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT} with {len(days)} days")


if __name__ == "__main__":
    main()
