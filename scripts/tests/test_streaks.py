"""Unit tests for the pure streak computation — no network involved."""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from contribution_data import Day
from streaks import compute_streaks


def _days(spec: str, start: dt.date) -> list[Day]:
    """`spec` is a string of 0/1 digits, one per day starting at `start`;
    '1' means "contributed", any other char means a count of that digit.
    """
    return [
        Day(date=start + dt.timedelta(days=i), count=int(ch))
        for i, ch in enumerate(spec)
    ]


def test_empty_history_has_no_streaks():
    summary = compute_streaks([], today=dt.date(2026, 1, 1))
    assert summary.current.length == 0
    assert summary.longest.length == 0


def test_current_streak_counts_back_from_today():
    start = dt.date(2026, 1, 1)
    days = _days("0011100111", start)  # today = start + 9, ends "111"
    summary = compute_streaks(days, today=start + dt.timedelta(days=9))
    assert summary.current.length == 3
    assert summary.current.end == start + dt.timedelta(days=9)
    assert summary.current.start == start + dt.timedelta(days=7)


def test_zero_contributions_today_gets_grace_period():
    start = dt.date(2026, 1, 1)
    days = _days("1110", start)  # today (index 3) is 0, yesterday ends a run of 3
    summary = compute_streaks(days, today=start + dt.timedelta(days=3))
    assert summary.current.length == 3
    assert summary.current.end == start + dt.timedelta(days=2)


def test_broken_streak_before_today_resets_to_zero():
    start = dt.date(2026, 1, 1)
    days = _days("1110011", start)  # gap at index 3-4, today (index 6) has activity
    summary = compute_streaks(days, today=start + dt.timedelta(days=6))
    assert summary.current.length == 2  # only counts back from today through the gap


def test_longest_streak_finds_the_longest_run_anywhere():
    start = dt.date(2026, 1, 1)
    days = _days("11000111100", start)
    summary = compute_streaks(days, today=start + dt.timedelta(days=10))
    assert summary.longest.length == 4
    assert summary.longest.start == start + dt.timedelta(days=5)
    assert summary.longest.end == start + dt.timedelta(days=8)


def test_single_contributing_day_is_a_streak_of_one():
    start = dt.date(2026, 1, 1)
    days = _days("1", start)
    summary = compute_streaks(days, today=start)
    assert summary.current.length == 1
    assert summary.longest.length == 1
