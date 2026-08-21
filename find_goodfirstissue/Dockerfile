# NOTE: build this from the PROJECT ROOT (the folder containing both
# backend/ and frontend/), not from inside backend/, e.g.:
#   gcloud run deploy issue-finder-backend --source . --region us-central1 \
#     --allow-unauthenticated
# run from issue-finder/ (the parent of backend/ and frontend/), and
# rename/copy this file to issue-finder/Dockerfile first.

FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (better Docker layer caching)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy backend code
COPY backend/ .

# Copy the frontend so Flask can serve it (templates/ and static/)
COPY frontend/ /frontend

# Cloud Run injects the PORT env var (usually 8080) — gunicorn must bind to it
ENV PORT=8080
EXPOSE 8080

# gunicorn is a production-grade server (app.run() from Flask is dev-only)
CMD exec gunicorn --bind :$PORT --workers 2 --threads 4 --timeout 0 app:app
