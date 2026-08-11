"""Streak graphic: current and longest streak, each with its date range.

Both figures are scoped to the same trailing-365-day window the other
graphics use (see contribution_data.py) rather than full account history,
so the numbers here are internally consistent with stats.svg and year.svg.
"""
from __future__ import annotations

from formatting import format_int, format_range
from streaks import StreakSummary
from svg_kit import THEMES, svg_document, xml_escape

WIDTH, HEIGHT = 480, 120
COLUMN_X = [24, 252]


def _column(x: int, label: str, length: int, date_range: str, theme: dict) -> str:
    unit = "day" if length == 1 else "days"
    return f"""
  <text x="{x}" y="34" font-size="12" fill="{theme['dim']}">{xml_escape(label)}</text>
  <text x="{x}" y="70" font-size="34" font-weight="700" fill="{theme['fg']}">{format_int(length)}</text>
  <text x="{x + (40 if length >= 10 else 26)}" y="70" font-size="13" fill="{theme['dim']}">{unit}</text>
  <text x="{x}" y="92" font-size="11" fill="{theme['dim']}">{xml_escape(date_range)}</text>
"""


def build_streak_svg(login: str, summary: StreakSummary, theme_name: str) -> str:
    theme = THEMES[theme_name]

    body = _column(COLUMN_X[0], "current streak", summary.current.length,
                    format_range(summary.current.start, summary.current.end), theme)
    body += _column(COLUMN_X[1], "longest streak", summary.longest.length,
                     format_range(summary.longest.start, summary.longest.end), theme)
    body += f'  <line x1="{COLUMN_X[1] - 24}" y1="20" x2="{COLUMN_X[1] - 24}" y2="{HEIGHT - 20}" stroke="{theme["rule"]}" stroke-width="1"/>\n'

    return svg_document(WIDTH, HEIGHT, body, theme_name, f"{login}'s contribution streaks")
