"""Guards against the bug this repo actually hit once: a RAMP character
missing from the embedded font's subset silently falls back to a system
font, which on Windows renders '`'/'='/'*' in a colored symbol font instead
of the theme's monochrome text — invisible in the SVG source, only visible
when rendered.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_font_subsets import CHARSET
from svg_kit import RAMP


def test_font_subset_covers_every_ramp_character():
    missing = [ch for ch in RAMP if ch not in CHARSET]
    assert not missing, f"RAMP characters missing from font CHARSET: {missing!r}"
