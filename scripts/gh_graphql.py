"""Minimal GitHub GraphQL client. Standard library only — no dependencies to
break in CI. Raises on transport errors, HTTP errors, and GraphQL error
payloads so failures are loud instead of silently producing empty stats.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

API_URL = "https://api.github.com/graphql"


class GraphQLError(RuntimeError):
    """Raised when the GitHub API rejects the request or returns errors."""


def run_query(query: str, variables: dict, token: str) -> dict:
    if not token:
        raise GraphQLError("no token provided (expected GITHUB_TOKEN)")

    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "User-Agent": "profile-stats-generator",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise GraphQLError(f"HTTP {exc.code} from GitHub API: {detail}") from exc
    except urllib.error.URLError as exc:
        raise GraphQLError(f"could not reach GitHub API: {exc.reason}") from exc

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise GraphQLError(f"GitHub API returned non-JSON response: {body[:200]!r}") from exc

    if "errors" in parsed and parsed["errors"]:
        raise GraphQLError(f"GraphQL errors: {parsed['errors']}")
    if "data" not in parsed:
        raise GraphQLError(f"GraphQL response missing 'data': {parsed}")

    return parsed["data"]
