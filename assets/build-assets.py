#!/usr/bin/env python3
"""Build the header banner and the card icons for the GitHub profile README.

    python3 assets/build-assets.py

Each image is written as HTML and rendered to PNG with headless Chrome.
GitHub serves README images through its camo proxy, so an SVG with text would be
drawn with the viewer's fonts. A pre-rendered PNG looks the same everywhere.

Icons: Lucide (lucide-static 0.460.0, ISC license, see assets/icons/LICENSE).
"""
import math
import pathlib
import random
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

BG = "#0e0f11"
INK = "#f4f4f5"
MUTED = "#9a9ca3"
LINE = "#3a3d44"
ORANGE = "#ff6a00"
ORANGE_SOFT = "#ff9a4d"

# Cards: published file name -> Lucide icon
CARDS = {
    "edinet-ma-ledger": "handshake",
    "holmesvau": "cctv",
    "mugicha": "gamepad-2",
    "shift-maker": "dna",
    "gmail-mcp": "mail",
    "todo-to-google-calendar": "calendar-check",
    "generative-agents-fire": "users",
    "fire-escape": "door-open",
}


def render(html: str, out: pathlib.Path, width: int, height: int, scale: int = 2) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        src = pathlib.Path(tmp) / "page.html"
        src.write_text(html, encoding="utf-8")
        subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             f"--force-device-scale-factor={scale}",
             f"--window-size={width},{height}",
             "--default-background-color=00000000",
             f"--screenshot={out}", src.as_uri()],
            check=True, capture_output=True,
        )
    print("wrote", out.relative_to(ROOT.parent))


def series() -> list[float]:
    """A quiet signal with one excursion, like a sensor reading with an anomaly."""
    rnd = random.Random(7)
    ys = []
    for i in range(64):
        base = 0.08 * math.sin(i / 3.1) + rnd.uniform(-0.06, 0.06)
        bump = 0.85 * math.exp(-((i - 43) / 3.2) ** 2)
        ys.append(base + bump)
    return ys


def banner() -> None:
    W, H = 1600, 400
    x0, x1, top, bottom = 930, 1510, 92, 300
    ys = series()
    lo, hi = -0.25, 1.0
    pts = [(x0 + (x1 - x0) * i / (len(ys) - 1),
            bottom - (bottom - top) * (y - lo) / (hi - lo)) for i, y in enumerate(ys)]
    path = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (x, y) in enumerate(pts))
    a, b = 37, 50
    hot = " ".join(f"{'M' if i == a else 'L'}{x:.1f},{y:.1f}" for i, (x, y) in enumerate(pts) if a <= i <= b)
    peak = min(pts[a:b + 1], key=lambda p: p[1])
    band_top = bottom - (bottom - top) * (0.16 - lo) / (hi - lo)
    band_bot = bottom - (bottom - top) * (-0.16 - lo) / (hi - lo)
    box_l, box_r = pts[a][0] - 6, pts[b][0] + 6

    html = f"""<!doctype html><meta charset="utf-8"><style>
html,body{{margin:0;width:{W}px;height:{H}px;background:{BG};overflow:hidden}}
.t{{position:absolute;left:104px;font-family:'Avenir Next',sans-serif}}
.k{{top:104px;font-size:19px;font-weight:600;letter-spacing:.22em;color:{ORANGE}}}
.n{{top:128px;font-size:116px;font-weight:700;letter-spacing:-.01em;color:{INK}}}
.s{{top:286px;font-size:27px;font-weight:500;color:{MUTED}}}
svg{{position:absolute;inset:0}}
</style>
<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{ORANGE_SOFT}"/><stop offset="1" stop-color="{ORANGE}"/></linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="7"/></filter>
    <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.1" fill="#1d1f24"/></pattern>
  </defs>
  <rect width="{W}" height="{H}" fill="url(#dots)"/>
  <rect x="{x0}" y="{band_top:.1f}" width="{x1 - x0}" height="{band_bot - band_top:.1f}" fill="#16181c"/>
  <line x1="{x0}" x2="{x1}" y1="{bottom + 22}" y2="{bottom + 22}" stroke="{LINE}" stroke-width="1.5"/>
  <rect x="{box_l:.1f}" y="{top - 26}" width="{box_r - box_l:.1f}" height="{bottom - top + 48}" fill="none" stroke="{LINE}" stroke-width="1.5" stroke-dasharray="5 5"/>
  <path d="{path}" fill="none" stroke="#5b5f68" stroke-width="2.4" stroke-linejoin="round"/>
  <path d="{hot}" fill="none" stroke="{ORANGE}" stroke-width="9" stroke-linejoin="round" stroke-linecap="round" filter="url(#glow)" opacity=".55"/>
  <path d="{hot}" fill="none" stroke="url(#g)" stroke-width="4.5" stroke-linejoin="round" stroke-linecap="round"/>
  <circle cx="{peak[0]:.1f}" cy="{peak[1]:.1f}" r="13" fill="none" stroke="{ORANGE}" stroke-width="2.5"/>
  <circle cx="{peak[0]:.1f}" cy="{peak[1]:.1f}" r="4.5" fill="{ORANGE}"/>
</svg>
<div class="t k">FOUNDER &amp; CEO, ASMIRAI L.L.C.</div>
<div class="t n">Kuchiki</div>
<div class="t s">Practical AI and data systems, built in Kumamoto, Japan.</div>
"""
    render(html, ROOT / "banner.png", W, H)


def icon(name: str, lucide: str) -> None:
    svg = (ROOT / "icons" / f"{lucide}.svg").read_text()
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r'width="24"\s+height="24"', 'width="34" height="34"', svg)
    svg = svg.replace('stroke-width="2"', 'stroke-width="1.75"')
    size = 64
    html = f"""<!doctype html><meta charset="utf-8"><style>
html,body{{margin:0;width:{size}px;height:{size}px;background:transparent}}
.tile{{width:{size}px;height:{size}px;border-radius:16px;background:{BG};
display:flex;align-items:center;justify-content:center;color:{ORANGE};
box-shadow:inset 0 0 0 1px #2a2c31}}
</style><div class="tile">{svg}</div>"""
    render(html, ROOT / "cards" / f"{name}.png", size, size)


if __name__ == "__main__":
    (ROOT / "cards").mkdir(exist_ok=True)
    banner()
    for name, lucide in CARDS.items():
        icon(name, lucide)
