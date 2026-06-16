# MovieLens Backend

FastAPI + SQLite backend for the MovieLens "latest-small" web application.

## Requirements

- Python 3.10+
- The bundled dataset `ml-latest-small.zip` (already in this directory)

## Setup

```bash
cd backend

# (recommended) create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# install dependencies
pip install -r requirements.txt
```

## Create the database

The database (`movielens.db`) is built automatically the first time the server
starts. You can also build it explicitly:

```bash
python src/setup_db.py
```

This extracts `ml-latest-small.zip` and loads the `movies`, `ratings`, and
`tags` tables. The dataset and the generated `movielens.db` are kept in
`backend/` (next to this README), separate from the source code in `src/`.

## Reset the database

To restore a clean dataset (e.g. after adding test movies), delete the DB and
rebuild it from the bundled data:

```bash
python src/reset_db.py
```

This deletes `movielens.db` and rebuilds it via the same `initialize_db()` used
on first startup. (Equivalent to `rm movielens.db && python src/setup_db.py`.)

## Run the server

```bash
python src/main.py
```

The API listens on **port 3000** with base path **`/movielens/api`**.
Interactive docs are available at <http://localhost:3000/docs>.

(Equivalent: `uvicorn main:app --app-dir src --host 0.0.0.0 --port 3000`.)

## API

Base URL: `http://localhost:3000/movielens/api`

| Method | Path                     | Description                                   |
|--------|--------------------------|-----------------------------------------------|
| GET    | `/movies?search={kw}`    | Search movies by title (case-insensitive)     |
| GET    | `/ratings/{movieId}`     | All ratings for a movie                       |
| POST   | `/movies`                | Add a movie `{title, genres}` → `{movieId}`   |
| POST   | `/recommendations`       | Recommendations from `{ratings:[{movieId,rating}]}` |
<!-- ---------- tag search endpoint table row starts ---------- -->
| POST   | `/tags/movies`           | Movies with at least one matching tag from `{search}` |
<!-- ---------- tag search endpoint table row finishes ---------- -->

### Recommendation algorithm

User-based collaborative filtering (`recommender.py`):

1. Find DB users who co-rated the movies the user supplied.
2. `sim(u, v)` = Pearson correlation over co-rated items.
3. Keep the top-`K` most similar users (`K = 30`).
4. Predict each unseen movie's rating with the mean-centered weighted average
   `r̂(u,i) = r̄_u + Σ sim(u,v)·(r_{v,i} − r̄_v) / Σ |sim(u,v)|`.
5. Return the top-`N` movies (`N = 10`).

<!-- ---------- tag search docs starts ---------- -->
### Tag-based movie search

`POST /tags/movies` accepts `{ "search": "keyword" }` and returns movies
that have at least one matching user-provided tag. Matching is
case-insensitive. Keywords shorter than 5 characters must equal the whole tag;
keywords with at least 5 characters match the first 5 characters of the tag.
<!-- ---------- tag search docs finishes ---------- -->

## Project layout

```
backend/
├── src/                     # all Python source code
│   ├── main.py              # FastAPI app, CORS, router wiring, uvicorn entrypoint
│   ├── db.py                # paths + get_db() connection helper + first-run init
│   ├── setup_db.py          # create & populate the SQLite DB from the CSVs
│   ├── models.py            # Pydantic request models
│   ├── recommender.py       # collaborative-filtering recommendation algorithm
│   └── routes/
│       ├── movies.py        # /movies, /ratings/{movieId}
│       └── recommendations.py  # /recommendations
├── requirements.txt
├── README.md
└── ml-latest-small.zip      # bundled dataset (DB + extracted CSVs generated here)
```
