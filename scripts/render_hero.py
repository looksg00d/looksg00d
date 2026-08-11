"""Hero graphic: total contributions + a weekly-aggregate sparkline.

Deliberately a column-free area chart over *weekly* sums, not daily counts —
daily contributions are sparse and discrete, so a line through them would
claim values that never existed. Weekly aggregates are dense enough that a
continuous line is defensible (see README, "Pick the right chart type").
"""
from __future__ import annotations

from contribution_data import ProfileData
from formatting import format_int
from svg_kit import THEMES, svg_document, xml_escape

WIDTH, HEIGHT = 480, 160
PLOT_LEFT, PLOT_RIGHT = 24, 456
PLOT_TOP, PLOT_BOTTOM = 96, 136


def _sparkline_path(weekly_totals: list[int]) -> tuple[str, str]:
    if not weekly_totals:
        return "", ""

    max_total = max(weekly_totals) or 1
    n = len(weekly_totals)
    span = PLOT_RIGHT - PLOT_LEFT
    step = span / max(n - 1, 1)

    points = []
    for i, total in enumerate(weekly_totals):
        x = PLOT_LEFT + i * step
        y = PLOT_BOTTOM - (total / max_total) * (PLOT_BOTTOM - PLOT_TOP)
        points.append((x, y))

    line_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    area_d = (
        f"M {points[0][0]:.1f},{PLOT_BOTTOM} "
        + " L ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        + f" L {points[-1][0]:.1f},{PLOT_BOTTOM} Z"
    )
    return line_d, area_d


def build_hero_svg(data: ProfileData, theme_name: str) -> str:
    theme = THEMES[theme_name]
    weekly_totals = [w.total for w in data.weeks]
    line_d, area_d = _sparkline_path(weekly_totals)

    if data.window_from.year == data.window_to.year:
        subtitle = "contributions in the last 365 days"
    else:
        subtitle = f"contributions, {data.window_from.year}–{data.window_to.year}"

    body = f"""
  <text x="24" y="52" font-size="40" font-weight="700" fill="{theme['fg']}">{format_int(data.total_contributions)}</text>
  <text x="24" y="74" font-size="13" fill="{theme['dim']}">{xml_escape(subtitle)}</text>
  <line x1="{PLOT_LEFT}" y1="{PLOT_BOTTOM}" x2="{PLOT_RIGHT}" y2="{PLOT_BOTTOM}" stroke="{theme['rule']}" stroke-width="1"/>
  <path d="{area_d}" fill="{theme['accent']}" opacity="0.15"/>
  <path d="{line_d}" fill="none" stroke="{theme['accent']}" stroke-width="1.6"/>
  <text x="{PLOT_LEFT}" y="{PLOT_BOTTOM + 16}" font-size="10" fill="{theme['dim']}">{xml_escape(data.window_from.isoformat())}</text>
  <text x="{PLOT_RIGHT}" y="{PLOT_BOTTOM + 16}" font-size="10" fill="{theme['dim']}" text-anchor="end">{xml_escape(data.window_to.isoformat())}</text>
"""
    return svg_document(WIDTH, HEIGHT, body, theme_name, f"{data.login}'s contribution activity")
