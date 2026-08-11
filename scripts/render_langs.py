"""Top-languages graphic: ranked bars by byte share, annotated with how many
public repos each language appears in — the two metrics the article calls
out ("top languages, by bytes and by repo") side by side on one row instead
of two separate lists.
"""
from __future__ import annotations

from contribution_data import Language
from svg_kit import THEMES, svg_document, xml_escape

WIDTH = 480
ROW_HEIGHT = 28
TOP_MARGIN = 20
MAX_ROWS = 6

BAR_X = 140
BAR_MAX_W = 170  # leaves room for the widest label ("100.0% · 18 repos") to
                 # the right without overlapping a near-full-width bar


def build_langs_svg(login: str, languages: list[Language], theme_name: str) -> str:
    theme = THEMES[theme_name]
    top = languages[:MAX_ROWS]
    height = TOP_MARGIN + ROW_HEIGHT * max(len(top), 1) + 12

    if not top:
        body = f'  <text x="24" y="{TOP_MARGIN + 20}" font-size="13" fill="{theme["dim"]}">no public repositories with detected languages</text>\n'
        return svg_document(WIDTH, height, body, theme_name, f"{login}'s top languages")

    total_bytes = sum(lang.bytes_ for lang in top) or 1
    max_bytes = top[0].bytes_ or 1

    rows = []
    for i, lang in enumerate(top):
        y = TOP_MARGIN + i * ROW_HEIGHT
        bar_w = max(2, (lang.bytes_ / max_bytes) * BAR_MAX_W)
        share = 100 * lang.bytes_ / total_bytes
        repo_word = "repo" if lang.repo_count == 1 else "repos"
        rows.append(f"""
  <text x="24" y="{y + 14}" font-size="12" fill="{theme['fg']}">{xml_escape(lang.name)}</text>
  <rect x="{BAR_X}" y="{y + 3}" width="{BAR_MAX_W}" height="10" rx="3" fill="{theme['rule']}"/>
  <rect x="{BAR_X}" y="{y + 3}" width="{bar_w:.1f}" height="10" rx="3" fill="{xml_escape(lang.color)}"/>
  <text x="{WIDTH - 24}" y="{y + 12}" font-size="11" fill="{theme['dim']}" text-anchor="end">{share:.1f}% · {lang.repo_count} {repo_word}</text>
""")

    body = "".join(rows)
    return svg_document(WIDTH, height, body, theme_name, f"{login}'s top languages")
