"""Character grid → typing-animation SVG.

Each row sits behind a clipPath rect that animates width 0 → full, with a
small block riding the wipe edge as a cursor. Rows stagger top to bottom
(`begin="{i * ROW_STAGGER}s"`) and every animation uses fill="freeze" so the
portrait prints once and stops — no looping, no JS (GitHub strips <script>
from rendered README markdown; SMIL survives).

The grid bakes in an advance width of exactly 0.600em (CHAR_W at
FONT_SIZE) to match JetBrains Mono's metrics — see svg_kit.py. Any other
monospace font substituted here would need CHAR_W recomputed or portraits
render narrower/wider than the grid assumes.
"""
from __future__ import annotations

from portrait_data import CharGrid
from svg_kit import THEMES, svg_document, xml_escape

FONT_SIZE = 12.9
CHAR_W = 7.74   # FONT_SIZE * 0.600 — JetBrains Mono's advance width
CHAR_H = 15.0
ROW_STAGGER = 0.09
WIPE_DURATION = 0.6
CURSOR_W = 2.0


def _row_svg(y: int, text: str, row_width: float, delay: float, theme: dict) -> str:
    escaped = xml_escape(text)
    clip_id = f"wipe-{y}"
    return f"""
  <clipPath id="{clip_id}">
    <rect x="0" y="{y}" width="0" height="{CHAR_H}">
      <animate attributeName="width" from="0" to="{row_width:.1f}"
               begin="{delay:.2f}s" dur="{WIPE_DURATION}s" fill="freeze" />
    </rect>
  </clipPath>
  <text x="0" y="{y + CHAR_H - 3:.1f}" font-size="{FONT_SIZE}" fill="{theme['fg']}"
        clip-path="url(#{clip_id})" xml:space="preserve">{escaped}</text>
  <rect y="{y}" width="{CURSOR_W}" height="{CHAR_H}" fill="{theme['accent']}">
    <animate attributeName="x" from="0" to="{row_width:.1f}"
             begin="{delay:.2f}s" dur="{WIPE_DURATION}s" fill="freeze" />
    <animate attributeName="opacity" from="1" to="0"
             begin="{delay + WIPE_DURATION:.2f}s" dur="0.01s" fill="freeze" />
  </rect>
"""


def build_portrait_svg(grid: CharGrid, theme_name: str, login: str) -> str:
    theme = THEMES[theme_name]
    row_width = grid.cols * CHAR_W

    rows_svg = []
    for i, row_text in enumerate(grid.rows):
        y = round(i * CHAR_H)
        delay = i * ROW_STAGGER
        rows_svg.append(_row_svg(y, row_text, row_width, delay, theme))

    width = round(row_width) + 4
    height = round(len(grid.rows) * CHAR_H) + 4
    body = "".join(rows_svg)

    return svg_document(width, height, body, theme_name, f"ASCII portrait of {login}")
