"""Year heatmap: one character per day, using the ASCII portrait's own
13-step ramp instead of GitHub's colored squares — same visual language,
drawn with the same embedded font.
"""
from __future__ import annotations

import datetime as dt

from contribution_data import ProfileData, Week
from formatting import month_label
from svg_kit import THEMES, ramp_char, svg_document, xml_escape

CHAR_W, CHAR_H = 12, 13
LEFT_MARGIN = 8
TOP_MARGIN = 30
ROWS = 7


def _weekday_row(day_date: dt.date) -> int:
    """GitHub buckets weeks Sunday-first; Python's date.weekday() is
    Monday-first, so shift by one to line rows up with GitHub's own grid.
    """
    return (day_date.weekday() + 1) % 7


def _month_labels(weeks: list[Week]) -> list[tuple[int, str]]:
    labels: list[tuple[int, str]] = []
    last_month = None
    for col, week in enumerate(weeks):
        first_of_month = next((d for d in week.days if d.date.day == 1), None)
        if first_of_month is None:
            continue
        month = first_of_month.date.month
        if month != last_month:
            labels.append((col, month_label(first_of_month.date)))
            last_month = month
    return labels


def build_year_svg(data: ProfileData, theme_name: str) -> str:
    theme = THEMES[theme_name]
    weeks = data.weeks
    grid_w = LEFT_MARGIN + len(weeks) * CHAR_W + 12
    max_count = max((d.count for w in weeks for d in w.days), default=0)

    cells = []
    for col, week in enumerate(weeks):
        x = LEFT_MARGIN + col * CHAR_W
        for day in week.days:
            row = _weekday_row(day.date)
            y = TOP_MARGIN + row * CHAR_H
            char = ramp_char(day.count, max_count)
            if char == " ":
                continue
            title = f"{day.date.isoformat()}: {day.count} contribution{'s' if day.count != 1 else ''}"
            cells.append(
                f'<text x="{x}" y="{y}" font-size="13" fill="{theme["fg"]}">'
                f'<title>{xml_escape(title)}</title>{xml_escape(char)}</text>'
            )

    month_cols = _month_labels(weeks)
    labels = [
        f'<text x="{LEFT_MARGIN + col * CHAR_W}" y="16" font-size="10" fill="{theme["dim"]}">{xml_escape(name)}</text>'
        for col, name in month_cols
    ]

    legend_y = TOP_MARGIN + ROWS * CHAR_H + 20
    legend_levels = [0, max_count * 0.25, max_count * 0.5, max_count * 0.75, max_count]
    legend_chars = "".join(ramp_char(v, max_count) for v in legend_levels)
    legend = f"""
  <text x="{LEFT_MARGIN}" y="{legend_y}" font-size="11" fill="{theme['dim']}">less</text>
  <text x="{LEFT_MARGIN + 34}" y="{legend_y}" font-size="13" fill="{theme['fg']}" letter-spacing="4">{xml_escape(legend_chars)}</text>
  <text x="{LEFT_MARGIN + 34 + len(legend_chars) * 12}" y="{legend_y}" font-size="11" fill="{theme['dim']}">more</text>
"""

    body = "\n".join(labels) + "\n" + "\n".join(cells) + legend
    height = legend_y + 12
    return svg_document(grid_w, height, body, theme_name, f"{data.login}'s contributions in the last year")
