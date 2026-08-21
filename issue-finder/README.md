# Unassigned Issue Finder

Finds recently created, open, **unassigned** GitHub issues labeled for
outside help (e.g. `good first issue`, `help wanted`) — a full-stack
app: Flask backend + vanilla JS/HTML frontend, both served together.

## Project structure

```
issue-finder/
├── backend/
│   ├── app.py              # Flask app + API routes
│   ├── github_client.py    # GitHub Search API wrapper
│   └── requirements.txt
└── frontend/
    ├── templates/
    │   └── index.html
    └── static/
        ├── css/style.css
        └── js/app.js
```

## Setup

1. **Get a GitHub token** (recommended — raises your rate limit a lot):
   https://github.com/settings/tokens → "Generate new token (classic)"
   → no scopes needed for public repo search.

2. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Set your token as an environment variable:**
   ```bash
   export GITHUB_TOKEN=ghp_yourtokenhere
   ```

4. **Run the server:**
   ```bash
   python app.py
   ```

5. Open **http://localhost:5000** in your browser. The page auto-searches
   on load with the default filters (good first issue / help wanted,
   last 30 days).

## API

`GET /api/search`

| Param        | Default                          | Description                          |
|--------------|-----------------------------------|---------------------------------------|
| `labels`     | `good first issue,help wanted`    | Comma-separated label list            |
| `language`   | (none)                            | Filter by repo language               |
| `days`       | `30`                               | Only issues created in last N days    |
| `min_stars`  | `0`                                 | Minimum repo star count               |
| `max_results`| `50` (capped at 100)               | Max issues to return                  |

Returns:
```json
{
  "query": "is:issue is:open no:assignee label:\"help wanted\" ...",
  "count": 12,
  "issues": [
    {
      "id": 123,
      "title": "...",
      "issue_url": "https://github.com/...",
      "repo_url": "https://github.com/owner/repo",
      "repo_full_name": "owner/repo",
      "labels": ["help wanted"],
      "created_at": "2026-08-10T12:00:00Z",
      "updated_at": "2026-08-11T09:00:00Z",
      "comments": 2,
      "body_snippet": "..."
    }
  ]
}
```

`GET /api/health` — returns `{"status": "ok", "token_configured": true/false}`

## Notes / next steps

- Results are cached in-memory for 2 minutes per unique query to avoid
  hammering the GitHub API on repeated page loads.
- GitHub's Search API caps results at 1000 per query (10 pages × 100) —
  fine for this use case.
- To deploy: any host that runs Flask works (Render, Railway, a VPS).
  Set `GITHUB_TOKEN` as an env var there too, and consider swapping the
  in-memory cache for Redis if you get real traffic.
- Nice additions: daily digest emails, repo "health" filters (last
  commit date, contributor count), a `Dockerfile` for one-command deploy.
