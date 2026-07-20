from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run(name: str) -> None:
    subprocess.run([sys.executable, str(SCRIPTS / name)], check=True, cwd=ROOT)


if __name__ == "__main__":
    run("make_portrait_panel.py")
    run("make_info_card.py")
    run("render_heatmap_svg.py")
