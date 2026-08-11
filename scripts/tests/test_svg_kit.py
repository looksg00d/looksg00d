"""Unit tests for the ramp-character mapping used by the year heatmap."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from svg_kit import RAMP, ramp_char


def test_zero_value_maps_to_blank():
    assert ramp_char(0, max_value=10) == RAMP[0]


def test_max_value_maps_to_densest_glyph():
    assert ramp_char(10, max_value=10) == RAMP[-1]


def test_zero_max_never_divides_by_zero():
    assert ramp_char(0, max_value=0) == RAMP[0]


def test_values_are_monotonic():
    levels = [RAMP.index(ramp_char(v, max_value=20)) for v in range(0, 21)]
    assert levels == sorted(levels)
