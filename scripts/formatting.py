"""Small text-formatting helpers shared by the render_*.py modules."""
from __future__ import annotations

import datetime as dt

_MONTHS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def format_int(n: int) -> str:
    return f"{n:,}"


def format_date(d: dt.date) -> str:
    return f"{_MONTHS[d.month - 1]} {d.day}, {d.year}"


def format_range(start: dt.date | None, end: dt.date | None) -> str:
    if start is None or end is None:
        return "—"
    if start == end:
        return format_date(start)
    if start.year == end.year:
        return f"{_MONTHS[start.month - 1]} {start.day} – {_MONTHS[end.month - 1]} {end.day}, {end.year}"
    return f"{format_date(start)} – {format_date(end)}"


def month_label(d: dt.date) -> str:
    return _MONTHS[d.month - 1]
