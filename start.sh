#!/bin/bash
# Start the MovieLens app: backend, frontend, or both.
#
# Usage:
#   ./start.sh backend     start the backend  (FastAPI, http://localhost:3000)
#   ./start.sh frontend    start the frontend (static files, http://localhost:8080)
#   ./start.sh both        start both together
#
# Press Ctrl+C to stop.

# Move to the folder this script is in, so the paths below work
# no matter where you run it from.
cd "$(dirname "$0")"

start_backend() {
  echo "Starting backend -> http://localhost:3000"
  cd backend
  source venv/bin/activate
  python src/main.py
}

start_frontend() {
  echo "Starting frontend -> http://localhost:8080"
  cd frontend
  python3 -m http.server 8080
}

if [ "$1" = "backend" ]; then
  start_backend
elif [ "$1" = "frontend" ]; then
  start_frontend
elif [ "$1" = "both" ]; then
  trap "kill 0" SIGINT          # Ctrl+C stops both at once
  start_backend &
  start_frontend
else
  echo "Usage: $0 backend | frontend | both"
  exit 1
fi
