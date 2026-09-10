# MovieLens backend

FastAPI + SQLite for `WebApp_Dev_Assignment_Spring_2026.pdf`.
The `september-exam` branch exposes only the four required API operations.

## Setup and run

Python 3.10+ is required. From the repository root:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

The tested direct dependency versions are pinned in `requirements.txt`.
SQLite, CSV import and the recommender use the Python standard library.

The API listens on port **3000**, under **`/movielens/api`**.
Open <http://localhost:3000/docs> for Swagger UI or
<http://localhost:3000/openapi.json> for the OpenAPI description.
The frontend runs separately: from the repository root, `./start.sh both`
after setup, then open <http://localhost:8080>.

## Database creation and reset

The bundled `ml-latest-small.zip` supplies the dataset; no download is needed.
On first startup, `initialize_db()` creates `movies`, `ratings` and `tags`
with the corresponding CSV columns and imports all data rows: **9,742 movies,
100,836 ratings, 3,683 tags**. The Spring assignment requires all three tables,
including `tags`, even though it has no tag-search endpoint.
Existing databases may contain added movies.

From `backend/`, `python src/setup_db.py` also initializes the database.
If the database already exists, it is preserved. Imports build a temporary
SQLite file, commit successfully and then replace the destination, so a failed
import cannot destroy a working database. Extracted CSVs and `movielens.db`
live in `backend/`; source code lives in `backend/src/`.

To **discard added movies** and restore the bundled dataset, stop the backend
first and run `python src/reset_db.py`. This is an explicit manual reset;
normal startup never resets existing data.

## API contract

Base URL: `http://localhost:3000/movielens/api`

| Method | Path | Input | Success response |
|---|---|---|---|
| GET | `/movies?search=...` | Query keyword; omitted/empty matches all | 200 `{status:"success", movies:[...]}` |
| GET | `/ratings/{movieId}` | Positive integer path ID | 200 `{status:"success", ratings:[...]}` |
| POST | `/movies` | `{title, genres}` | 201 `{status:"success", movieId:...}` |
| POST | `/recommendations` | `{ratings:[{movieId,rating}]}` | 200 `{status:"success", recommendations:[...]}` |

JSON bodies use double-quoted keys/strings. Example:

```json
{"ratings":[{"movieId":1,"rating":5},{"movieId":32,"rating":2}]}
```

Titles are searched by literal, Unicode case-insensitive substring. `%` and `_`
are ordinary characters, not wildcard operators. Results include all matches.
Movie IDs are allocated by SQLite's `INTEGER PRIMARY KEY`; duplicate titles
are allowed. Title/genres must contain non-whitespace text.

Ratings must be finite numeric values from 0.5 to 5 in half-star increments.
IDs must be positive JSON integers; numeric strings and booleans are rejected.
Duplicate input movie IDs are rejected. Invalid requests return **422** with
`detail` entries containing `loc`, `msg`, and `type`. Additional unknown model
fields are ignored under Pydantic's default policy.

An ID with no dataset ratings yields an empty list. Recommendation input IDs
are validated structurally, but not checked for database existence: unknown
IDs provide no overlap and still contribute to the input user's mean.
Submitted ratings are **never stored**. Browser ratings disappear on refresh.

## Recommendation algorithm

`recommender.py` follows the formula in the Spring assignment, page 3:

1. Find users with overlapping rated movies.
2. Compute Pearson over co-rated vectors, with means restricted to those vectors.
3. Retain the top **K=30** nonzero usable correlations, including negative ones.
4. For each unseen candidate, calculate
   `mean_u + sum(sim * (rating_vi - mean_v)) / sum(abs(sim))`.
5. Rank raw predictions, break ties by movie ID, and return at most **N=10**,
   rounded to two decimals.

The prediction uses the input user's overall mean and each neighbour's overall
dataset mean. Both sums include only neighbours who rated that candidate;
missing ratings are not zero. Fewer than two shared movies, zero variance or
no usable weights may produce an empty result. Zero correlation contributes
no weight and is omitted. Neighbour ties use user ID.

There is no extra support filter or score clamping. The formula can predict
outside the input scale 0.5-5; the frontend explains this. Empty, single-rating
and constant-score requests may legitimately return `[]`. The UI recommends
at least two familiar movies with different scores.

## Implementation map and limits

- `src/main.py`: FastAPI lifespan, safe validation-error JSON, CORS, routing,
  Uvicorn entry point. Blocking SQLite routes use `def` and FastAPI's thread pool.
- `src/models.py`: Pydantic request validation, not ORM tables.
- `src/db.py`: paths, casefold SQL function, connection cleanup. Writes commit
  explicitly; SQLite's connection context manager does not close the connection.
- `src/setup_db.py`, `src/reset_db.py`: dataset import and explicit replacement.
- `src/routes/`: only the four Spring API operations, in `movies.py` and
  `recommendations.py`.
- `src/recommender.py`: collaborative filtering, no request-rating writes.

This is a local classroom application without authentication, HTTPS configuration
or a reverse proxy. Wildcard CORS permits non-credentialed browser access;
it is not authorization. The frontend's API address is `API_BASE` in `index.js`.
Change it if the backend runs on a different host. Table relationships are
represented by IDs and joins; the schema does not declare foreign keys.

## Checks

Run from the repository root:

```bash
backend/venv/bin/python -m unittest discover -s backend/tests -v
node tests/frontend.cjs
node --check frontend/index.js
bash -n start.sh shutdown.sh
```

The backend checks use the real ASGI app and temporary databases, verify dataset
import, the exact Spring API contract, validation, CORS, absence of the former
tag-search endpoint, read-only recommendations and hand-calculated predictions.
The frontend checks cover error handling and local
state, including discarding outdated async results. Real rendering and browser
networking require browser verification; the Node checks do not simulate a DOM.

See [requirements check](../docs/requirements-check.md) and the
[Greek oral-exam guide](../notes/exam-prep/00-index.md).
