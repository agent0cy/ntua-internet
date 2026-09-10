# ntua-internet

Web-dev project for the Internet Applications course in ECE NTUA.

A web app over the MovieLens "latest-small" dataset: search movies, add movies,
rate them in page memory, view average ratings, and get personalized
recommendations. FastAPI + SQLite backend, vanilla HTML/CSS/JS frontend.

The `september-exam` branch implements only
`WebApp_Dev_Assignment_Spring_2026.pdf`. It has the four required API operations
and no exam extensions. The `tags` table is still imported because the Spring
assignment explicitly requires it. The version with tag search remains on `main`.

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
historical architecture diagrams; use the new exam guide below for current flows.

## Exam preparation

The Spring 2026 requirements are checked in
[docs/requirements-check.md](docs/requirements-check.md). The June tag-search
extension is absent from this branch's source code and UI.

- [Greek oral-exam PDF](output/pdf/MovieLens_Oral_Exam_Guide_GR.pdf): 168 questions
  with answers, 16 DevTools drills, worked recommendations and three mock exams.
- [Editable study notes and source map](notes/exam-prep/00-index.md).
- [Validation commands and API details](backend/README.md).

The study guide and PDF were written for `main`, which includes tag search.
Skip the June-extension sections and tag-search exercise on this branch; the
Spring API and general theory still apply. Older study aids and UML diagrams
describe earlier versions and have been preserved as historical material.

## Submission package

[`20012.zip`](20012.zip) contains the current `september-exam` source, including
the Pearson zero-correlation fix, without exam extensions. It includes the three
frontend files, backend source and setup instructions, dependencies, bundled
dataset, launch scripts, tests and license. The database is created on first
startup; virtual environments, generated files and study material are excluded.
See `backend/README.md` inside the archive for setup and validation commands.
The archive was checked after extraction into a clean folder; it has not been
submitted to the course.
