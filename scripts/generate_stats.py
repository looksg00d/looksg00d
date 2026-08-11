"""Entry point: fetch this profile's public GitHub data and (re)write the
stats SVGs. Standard library only at runtime — the font subsets are
pre-built and committed, so CI never needs fonttools installed.

Env vars (both required):
  GITHUB_TOKEN  auth for the GraphQL API. The workflow's built-in token is
                enough; it only ever sees public data for this login.
  GH_LOGIN      the GitHub username/org to report on.

Local run:
  GITHUB_TOKEN=$(gh auth token) GH_LOGIN=<you> python scripts/generate_stats.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from contribution_data import fetch_profile_data
from render_hero import build_hero_svg
from render_langs import build_langs_svg
from render_streak import build_streak_svg
from render_year import build_year_svg
from streaks import compute_streaks

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

GENERATORS = {
    "stats": lambda data, streaks_, theme: build_hero_svg(data, theme),
    "streak": lambda data, streaks_, theme: build_streak_svg(data.login, streaks_, theme),
    "langs": lambda data, streaks_, theme: build_langs_svg(data.login, data.languages, theme),
    "year": lambda data, streaks_, theme: build_year_svg(data, theme),
}


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN", "")
    login = os.environ.get("GH_LOGIN", "")

    if not token:
        print("error: GITHUB_TOKEN is not set", file=sys.stderr)
        return 1
    if not login:
        print("error: GH_LOGIN is not set", file=sys.stderr)
        return 1

    print(f"fetching profile data for {login}...")
    data = fetch_profile_data(login, token)
    streaks_ = compute_streaks(data.days, data.window_to)

    print(
        f"  {data.total_contributions} contributions, "
        f"{data.public_repo_count} public repos, "
        f"current streak {streaks_.current.length}d, "
        f"longest streak {streaks_.longest.length}d"
    )

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    for name, build in GENERATORS.items():
        for theme in ("light", "dark"):
            svg = build(data, streaks_, theme)
            out_path = ASSETS_DIR / f"{name}-{theme}.svg"
            out_path.write_text(svg, encoding="utf-8", newline="\n")
            print(f"  wrote {out_path.relative_to(ASSETS_DIR.parent)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
