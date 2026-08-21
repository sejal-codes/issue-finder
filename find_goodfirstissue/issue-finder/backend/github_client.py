"""
github_client.py
-----------------
Thin wrapper around the GitHub Search API for unassigned, open,
help-wanted-labeled issues. Kept separate from the Flask app so it
can be unit tested / reused (e.g. in a CLI or cron job) independently.
"""

import time
from datetime import datetime, timedelta

import requests

SEARCH_URL = "https://api.github.com/search/issues"


class GitHubAPIError(Exception):
    """Raised when the GitHub API returns an error we can't recover from."""

    def __init__(self, message, status_code=None, retry_after=None):
        super().__init__(message)
        self.status_code = status_code
        self.retry_after = retry_after


def build_query(labels=None, language=None, days=30, min_stars=0, extra=""):
    """Builds a GitHub search qualifier string."""
    labels = labels or ["good first issue", "help wanted"]
    parts = ["is:issue", "is:open", "no:assignee", "archived:false"]

    for label in labels:
        parts.append(f'label:"{label}"')

    if language:
        parts.append(f"language:{language}")

    if days:
        since = (datetime.utcnow() - timedelta(days=int(days))).strftime("%Y-%m-%d")
        parts.append(f"created:>={since}")

    if min_stars:
        parts.append(f"stars:>={int(min_stars)}")

    if extra:
        parts.append(extra)

    return " ".join(parts)


def search_issues(token=None, labels=None, language=None, days=30,
                   min_stars=0, max_results=50, sort="created", order="desc"):
    """
    Queries GitHub's search/issues endpoint and returns a normalized list
    of dicts. Raises GitHubAPIError on failure (rate limit, bad request, etc).
    """
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    query = build_query(labels, language, days, min_stars)

    results = []
    page = 1
    per_page = min(100, max_results)

    while len(results) < max_results and page <= 10:
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": per_page,
            "page": page,
        }
        resp = requests.get(SEARCH_URL, headers=headers, params=params, timeout=15)

        if resp.status_code == 403 and "rate limit" in resp.text.lower():
            reset = resp.headers.get("X-RateLimit-Reset")
            retry_after = None
            if reset:
                retry_after = max(int(reset) - int(time.time()), 0)
            raise GitHubAPIError(
                "GitHub API rate limit exceeded. Add a token or wait and retry.",
                status_code=403,
                retry_after=retry_after,
            )

        if resp.status_code == 422:
            raise GitHubAPIError(
                f"Invalid search query: {query}", status_code=422
            )

        if resp.status_code != 200:
            raise GitHubAPIError(
                f"GitHub API error {resp.status_code}: {resp.text[:200]}",
                status_code=resp.status_code,
            )

        data = resp.json()
        items = data.get("items", [])
        if not items:
            break

        results.extend(items)
        if len(items) < per_page:
            break
        page += 1

    return [_normalize(issue) for issue in results[:max_results]], query


def _normalize(issue):
    """Flattens a raw GitHub issue payload into just what the frontend needs."""
    repo_url = issue["repository_url"].replace(
        "https://api.github.com/repos/", "https://github.com/"
    )
    repo_full_name = issue["repository_url"].split("/repos/")[-1]
    return {
        "id": issue["id"],
        "title": issue["title"],
        "issue_url": issue["html_url"],
        "repo_url": repo_url,
        "repo_full_name": repo_full_name,
        "labels": [l["name"] for l in issue.get("labels", [])],
        "created_at": issue["created_at"],
        "updated_at": issue["updated_at"],
        "comments": issue["comments"],
        "body_snippet": (issue.get("body") or "")[:200],
    }
