"""Fetches and shapes the GitHub data the stats graphics are drawn from.

Two determinism traps this module exists to avoid (see README):
  1. The contribution window is pinned to whole UTC days, not "now minus a
     year", so two runs on the same UTC date always bucket days identically.
  2. Repositories are filtered to `privacy: PUBLIC` so the workflow's
     GITHUB_TOKEN and a maintainer's personal token never disagree.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

from gh_graphql import run_query

CONTRIBUTIONS_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { date contributionCount }
        }
      }
    }
  }
}
"""

REPOS_QUERY = """
query($login: String!, $after: String) {
  user(login: $login) {
    repositories(
      first: 50
      after: $after
      privacy: PUBLIC
      ownerAffiliations: [OWNER]
      isFork: false
    ) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        name
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


@dataclass(frozen=True)
class Day:
    date: dt.date
    count: int


@dataclass(frozen=True)
class Week:
    start: dt.date
    total: int
    days: list = field(default_factory=list)  # list[Day], Sunday-first, as GitHub buckets them


@dataclass(frozen=True)
class Language:
    name: str
    color: str
    bytes_: int
    repo_count: int


@dataclass(frozen=True)
class ProfileData:
    login: str
    window_from: dt.date
    window_to: dt.date
    total_contributions: int
    days: list = field(default_factory=list)   # list[Day], chronological
    weeks: list = field(default_factory=list)  # list[Week], chronological
    languages: list = field(default_factory=list)  # list[Language], by bytes desc
    public_repo_count: int = 0


def _contribution_window(today: dt.date) -> tuple[dt.date, dt.date]:
    return today - dt.timedelta(days=364), today


def _fetch_contributions(login: str, token: str, today: dt.date) -> tuple[dt.date, dt.date, int, list, list]:
    window_from, window_to = _contribution_window(today)
    variables = {
        "login": login,
        "from": f"{window_from.isoformat()}T00:00:00Z",
        "to": f"{window_to.isoformat()}T23:59:59Z",
    }
    data = run_query(CONTRIBUTIONS_QUERY, variables, token)
    user = data.get("user")
    if user is None:
        raise ValueError(f"GitHub user '{login}' not found or not accessible")

    calendar = user["contributionsCollection"]["contributionCalendar"]
    total = calendar["totalContributions"]

    days: list[Day] = []
    weeks: list[Week] = []
    for week in calendar["weeks"]:
        week_total = 0
        week_start = None
        week_days: list[Day] = []
        for entry in week["contributionDays"]:
            day_date = dt.date.fromisoformat(entry["date"])
            count = entry["contributionCount"]
            day = Day(date=day_date, count=count)
            days.append(day)
            week_days.append(day)
            week_total += count
            if week_start is None:
                week_start = day_date
        if week_start is not None:
            weeks.append(Week(start=week_start, total=week_total, days=week_days))

    return window_from, window_to, total, days, weeks


def _fetch_languages(login: str, token: str) -> tuple[list, int]:
    bytes_by_lang: dict[str, int] = {}
    color_by_lang: dict[str, str] = {}
    repos_by_lang: dict[str, int] = {}
    repo_count = 0
    cursor = None

    while True:
        data = run_query(REPOS_QUERY, {"login": login, "after": cursor}, token)
        user = data.get("user")
        if user is None:
            raise ValueError(f"GitHub user '{login}' not found or not accessible")

        repos = user["repositories"]
        if cursor is None:
            repo_count = repos["totalCount"]

        for repo in repos["nodes"]:
            langs_seen_in_repo = set()
            for edge in repo["languages"]["edges"]:
                name = edge["node"]["name"]
                bytes_by_lang[name] = bytes_by_lang.get(name, 0) + edge["size"]
                color_by_lang.setdefault(name, edge["node"]["color"] or "#888888")
                langs_seen_in_repo.add(name)
            for name in langs_seen_in_repo:
                repos_by_lang[name] = repos_by_lang.get(name, 0) + 1

        page_info = repos["pageInfo"]
        if not page_info["hasNextPage"]:
            break
        cursor = page_info["endCursor"]

    languages = [
        Language(name=name, color=color_by_lang[name], bytes_=total_bytes, repo_count=repos_by_lang[name])
        for name, total_bytes in bytes_by_lang.items()
    ]
    languages.sort(key=lambda lang: lang.bytes_, reverse=True)
    return languages, repo_count


def fetch_profile_data(login: str, token: str, today: dt.date | None = None) -> ProfileData:
    """Fetches everything the generators need in two GraphQL round trips
    (the second paginated). `today` is injectable for deterministic tests.
    """
    if not login:
        raise ValueError("login must not be empty")

    today = today or dt.datetime.now(dt.timezone.utc).date()

    window_from, window_to, total, days, weeks = _fetch_contributions(login, token, today)
    languages, repo_count = _fetch_languages(login, token)

    return ProfileData(
        login=login,
        window_from=window_from,
        window_to=window_to,
        total_contributions=total,
        days=days,
        weeks=weeks,
        languages=languages,
        public_repo_count=repo_count,
    )
