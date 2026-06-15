# ntua-internet

Web-dev project for the Internet Applications course in ECE NTUA.

A web app over the MovieLens "latest-small" dataset: search movies, add movies,
rate them (in-browser), view average ratings, and get personalized
recommendations. FastAPI + SQLite backend, vanilla HTML/CSS/JS frontend.

## Quick start

First-time setup (installs the backend dependencies into a virtualenv):

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..
```

Then start the app with the launcher script:

```bash
./start.sh backend     # backend only  -> http://localhost:3000
./start.sh frontend    # frontend only -> http://localhost:8080
./start.sh both        # both together (Ctrl+C stops both)
```

Open the frontend at <http://localhost:8080>. The database is built
automatically on the backend's first start.

## Project layout

```
.
├── start.sh            # one-command launcher (backend | frontend | both)
├── backend/            # FastAPI + SQLite (see backend/README.md)
│   └── src/            # Python source code
├── frontend/           # index.html / index.js / index.css (no frameworks)
└── docs/               # UML diagrams (Mermaid + PlantUML)
```

See [`backend/README.md`](backend/README.md) for API details and how to build or
reset the database, and [`docs/uml-diagrams.md`](docs/uml-diagrams.md) for the
architecture diagrams.
