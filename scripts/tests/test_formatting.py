"""Unit tests for date/number formatting helpers."""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from formatting import format_int, format_range


def test_format_int_adds_thousands_separators():
    assert format_int(1234567) == "1,234,567"
    assert format_int(29) == "29"


def test_format_range_collapses_single_day():
    d = dt.date(2026, 8, 11)
    assert format_range(d, d) == "Aug 11, 2026"


def test_format_range_same_year_omits_repeated_year():
    start, end = dt.date(2026, 8, 3), dt.date(2026, 8, 11)
    assert format_range(start, end) == "Aug 3 – Aug 11, 2026"


def test_format_range_spans_years():
    start, end = dt.date(2025, 12, 30), dt.date(2026, 1, 2)
    assert format_range(start, end) == "Dec 30, 2025 – Jan 2, 2026"


def test_format_range_handles_missing_dates():
    assert format_range(None, None) == "—"
