"""
app.py
------
Flask backend for the Unassigned Issue Finder.

Endpoints:
  GET  /api/search   -> search GitHub for unassigned, open, help-wanted issues
  GET  /api/health    -> simple health check
  GET  /                -> serves the frontend

Run:
  export GITHUB_TOKEN=ghp_xxxx   (optional but recommended)
  python app.py
"""

import os
import time

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

from github_client import search_issues, GitHubAPIError

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static",
)
CORS(app)  # allows the frontend to be served/hosted separately if you want

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

# --- extremely simple in-memory cache to avoid hammering the GitHub API
# on repeated identical searches (e.g. user re-loading the page) ---
_cache = {}
CACHE_TTL_SECONDS = 120


def _cache_key(params):
    return tuple(sorted(params.items()))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "token_configured": bool(GITHUB_TOKEN)})


@app.route("/api/search")
def api_search():
    labels_param = request.args.get("labels", "good first issue,help wanted")
    labels = [l.strip() for l in labels_param.split(",") if l.strip()]

    language = request.args.get("language", "").strip() or None
    days = request.args.get("days", 30)
    min_stars = request.args.get("min_stars", 0)
    max_results = request.args.get("max_results", 50)

    try:
        days = int(days)
        min_stars = int(min_stars)
        max_results = min(int(max_results), 100)  # hard cap to be a good API citizen
    except ValueError:
        return jsonify({"error": "days, min_stars, and max_results must be integers"}), 400

    cache_params = {
        "labels": labels_param,
        "language": language,
        "days": days,
        "min_stars": min_stars,
        "max_results": max_results,
    }
    key = _cache_key(cache_params)
    cached = _cache.get(key)
    if cached and (time.time() - cached["ts"]) < CACHE_TTL_SECONDS:
        return jsonify(cached["payload"])

    try:
        issues, query_used = search_issues(
            token=GITHUB_TOKEN,
            labels=labels,
            language=language,
            days=days,
            min_stars=min_stars,
            max_results=max_results,
        )
    except GitHubAPIError as e:
        status = e.status_code or 502
        body = {"error": str(e)}
        if e.retry_after is not None:
            body["retry_after_seconds"] = e.retry_after
        return jsonify(body), status

    payload = {
        "query": query_used,
        "count": len(issues),
        "issues": issues,
    }
    _cache[key] = {"ts": time.time(), "payload": payload}

    return jsonify(payload)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
