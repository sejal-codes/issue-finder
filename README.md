🔍 Unassigned Issue Finder

Find open-source issues you can actually contribute to — no more scrolling through claimed, stale, or abandoned tickets.

A full-stack web app that searches GitHub for open, unassigned, beginner-friendly issues, filtered by label, language, recency, and repo popularity — so you spend less time hunting and more time contributing.

🔗 Live demo →

✨ Why this exists

Finding a good first issue on GitHub usually means:

Opening 15 repos and checking if the "good first issue" tag is a lie
Discovering someone already claimed it three weeks ago
Realizing the repo's been dead since 2022

This app cuts through that by querying GitHub's Search API directly for issues that are:

✅ Open
✅ Unassigned
✅ Labeled for outside help (good first issue, help wanted, or your own custom labels)
✅ Filterable by language, minimum repo stars, and how recently they were created
🚀 Features
Live search against the GitHub Search API — no stale cached datasets
Custom label filtering — search any labels, not just the defaults
Language filter — narrow results to the stack you actually know
Recency & star filters — skip abandoned repos or find hidden-gem projects
Clean, dark-themed UI — fast to scan, mobile-friendly
Smart caching — 2-minute in-memory cache so repeated searches don't hammer the GitHub API
🖥️ Tech Stack
Layer	Tech
Backend	Python, Flask, Flask-CORS
Frontend	Vanilla JS, HTML, CSS
Data	GitHub Search API
Deployment	Docker → Render
📦 Project Structure
issue-finder/
├── backend/
│   ├── app.py              # Flask app + API routes
│   ├── github_client.py    # GitHub Search API wrapper
│   └── requirements.txt
├── frontend/
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── css/style.css
│       └── js/app.js
└── Dockerfile
🛠️ Run it locally
bash
git clone https://github.com/sejal-codes/issue-finder.git
cd issue-finder/backend
pip install -r requirements.txt

export GITHUB_TOKEN=ghp_yourtoken   # optional, but raises your rate limit a lot
python app.py

Open http://localhost:5000 — the app auto-searches on load with default filters.

📡 API Reference

GET /api/search

Param	Default	Description
labels	good first issue,help wanted	Comma-separated label list
language	(none)	Filter by repo language
days	30	Only issues created in the last N days
min_stars	0	Minimum repo star count
max_results	50 (capped at 100)	Max issues to return

GET /api/health — returns {"status": "ok", "token_configured": true/false}

☁️ Deployment

This app ships as a single Docker image and deploys cleanly to Render, Google Cloud Run, or any Docker-friendly host. The included Dockerfile builds and serves the Flask app with Gunicorn out of the box — no extra config needed.

🗺️ Roadmap
 OR-based label matching (currently ANDs multiple labels)
 Daily digest emails for saved searches
 Repo health signals (last commit date, contributor count)
 Save/bookmark favorite issues
🤝 Contributing

Found a bug or have an idea? Open an issue or PR — fittingly, this repo would love its own "good first issue" contributors.
