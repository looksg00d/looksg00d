"""Shared SVG building blocks: the embedded-font stylesheet, the light/dark
palettes, and small escaping/formatting helpers used by every render_*.py
module. Keeping this in one place means every graphic stays visually
consistent without copy-pasted CSS.
"""
from __future__ import annotations

import base64
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape  # re-exported for callers

FONTS_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"

# The 13-character ramp used by the ASCII portrait, reused here so the year
# heatmap and the portrait speak the same visual language.
RAMP = " .`:-=+*cs#%@"

THEMES = {
    "light": {
        "bg": "#ffffff",
        "fg": "#1b1f24",
        "dim": "#6e7781",
        "rule": "#d0d7de",
        "accent": "#0969da",
    },
    "dark": {
        "bg": "#0d1117",
        "fg": "#e6edf3",
        "dim": "#8b949e",
        "rule": "#30363d",
        "accent": "#58a6ff",
    },
}


def _load_font_b64(filename: str) -> str:
    path = FONTS_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(
            f"missing font subset {path} — run scripts/build_font_subsets.py first"
        )
    return base64.b64encode(path.read_bytes()).decode("ascii")


_REGULAR_B64 = None
_BOLD_B64 = None


def font_face_css() -> str:
    """Base64 data-URI @font-face rules. Cached per-process since every
    render_*.py call re-embeds the same two ~3.6KB subsets.
    """
    global _REGULAR_B64, _BOLD_B64
    if _REGULAR_B64 is None:
        _REGULAR_B64 = _load_font_b64("stats-regular.woff2")
    if _BOLD_B64 is None:
        _BOLD_B64 = _load_font_b64("stats-bold.woff2")

    return f"""
    @font-face {{
      font-family: 'Stats Mono';
      font-weight: 400;
      src: url(data:font/woff2;base64,{_REGULAR_B64}) format('woff2');
    }}
    @font-face {{
      font-family: 'Stats Mono';
      font-weight: 700;
      src: url(data:font/woff2;base64,{_BOLD_B64}) format('woff2');
    }}
    text {{ font-family: 'Stats Mono', ui-monospace, monospace; }}
    """


def svg_document(width: int, height: int, body: str, theme_name: str, title: str) -> str:
    theme = THEMES[theme_name]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{xml_escape(title)}">
  <title>{xml_escape(title)}</title>
  <style>
    {font_face_css()}
  </style>
  <rect width="{width}" height="{height}" rx="10" fill="{theme['bg']}" stroke="{theme['rule']}" stroke-width="1"/>
{body}
</svg>
"""


def ramp_char(value: float, max_value: float) -> str:
    """Maps a value in [0, max_value] onto the portrait's ramp characters."""
    if max_value <= 0:
        return RAMP[0]
    level = int(round((value / max_value) * (len(RAMP) - 1)))
    level = max(0, min(len(RAMP) - 1, level))
    return RAMP[level]
