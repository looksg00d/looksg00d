"""Pure streak computation, kept separate from data fetching so it can be
unit-tested without hitting the network.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


@dataclass(frozen=True)
class Streak:
    length: int
    start: dt.date | None
    end: dt.date | None


@dataclass(frozen=True)
class StreakSummary:
    current: Streak
    longest: Streak


def compute_streaks(days: list, today: dt.date) -> StreakSummary:
    """`days` must be chronologically ordered Day objects (date, count).

    Today's zero-contribution day gets a grace period — the day isn't over
    yet — so the current streak counts back from yesterday in that case
    instead of resetting to zero.
    """
    if not days:
        empty = Streak(length=0, start=None, end=None)
        return StreakSummary(current=empty, longest=empty)

    ordered = sorted(days, key=lambda d: d.date)

    longest = Streak(length=0, start=None, end=None)
    run_len = 0
    run_start = None
    for day in ordered:
        if day.count > 0:
            if run_len == 0:
                run_start = day.date
            run_len += 1
            if run_len > longest.length:
                longest = Streak(length=run_len, start=run_start, end=day.date)
        else:
            run_len = 0
            run_start = None

    end_index = len(ordered) - 1
    if ordered[end_index].date == today and ordered[end_index].count == 0:
        end_index -= 1  # today isn't over yet — don't count it as a break

    current_len = 0
    current_end = None
    i = end_index
    while i >= 0 and ordered[i].count > 0:
        if current_len == 0:
            current_end = ordered[i].date
        current_len += 1
        i -= 1
    current_start = ordered[i + 1].date if current_len > 0 else None
    current = Streak(length=current_len, start=current_start, end=current_end)

    return StreakSummary(current=current, longest=longest)
