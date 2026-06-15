#!/bin/bash
# Stop the MovieLens app: backend, frontend, or both.
#
# Usage:
#   ./shutdown.sh backend     stop the backend  (FastAPI on port 3000)
#   ./shutdown.sh frontend    stop the frontend (static files on port 8080)
#   ./shutdown.sh both        stop both

stop_backend() {
  pkill -f "src/main.py" && echo "Backend stopped." || echo "Backend was not running."
}

stop_frontend() {
  pkill -f "http.server 8080" && echo "Frontend stopped." || echo "Frontend was not running."
}

if [ "$1" = "backend" ]; then
  stop_backend
elif [ "$1" = "frontend" ]; then
  stop_frontend
elif [ "$1" = "both" ]; then
  stop_backend
  stop_frontend
else
  echo "Usage: $0 backend | frontend | both"
  exit 1
fi
