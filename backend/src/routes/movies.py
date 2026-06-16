"""
Movie + ratings endpoints.

  GET  /movies?search={keyword}   search movies by title (case-insensitive)
  GET  /ratings/{movieId}         all ratings for a movie
  POST /movies                    add a new movie

These are mounted under the `/movielens/api` prefix in main.py, so the full
paths are e.g. GET /movielens/api/movies.

────────────────────────────────────────────────────────────────────────────
THEORY · L4 Server-side/REST · HTTP as an API (verbs → CRUD)
  A key REST principle from the lecture is to "respect the original meaning of
  the HTTP verbs." This module demonstrates the verb→CRUD mapping directly:
    GET  /movies          → Read   (safe, no side effects)
    GET  /ratings/{id}    → Read
    POST /movies          → Create (sends data in the body, creates a resource)
  It also shows the three ways the lecture lists for passing input to an
  endpoint: the URL path, the URL query string, and the request body.
────────────────────────────────────────────────────────────────────────────
"""

from typing import Optional

from fastapi import APIRouter

from db import get_db
from models import MovieAdd

# THEORY · L4 · routers: APIRouter groups related endpoints; main.py attaches it
# under the shared `/movielens/api` prefix (the "Uniform Interface" / URL map).
router = APIRouter()


# THEORY · L4 · @app.get decorator + Query parameter:
#   The @router.get(...) decorator registers this function as the handler for
#   GET on this path (HTTP verb → Python function). `search` is NOT in the path,
#   so FastAPI automatically treats it as a QUERY-STRING parameter
#   (?search=...). `Optional[str] = None` makes it optional, so plain GET
#   /movies (no query) returns everything.
@router.get("/movies")
def search_movies(search: Optional[str] = None):
    """
    Return all movies whose title contains `search` (case-insensitive), or all
    movies when no keyword is given. SQLite's LIKE is already case-insensitive
    for ASCII text, which satisfies the spec.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        if search:
            # THEORY · L4 · parameterized query (SQL injection safety): the
            # user's keyword is bound via the `?` placeholder, never spliced
            # into the SQL string. LIKE with %...% wildcards = substring match.
            cursor.execute(
                "SELECT * FROM movies WHERE title LIKE ?", (f"%{search}%",)
            )
        else:
            cursor.execute("SELECT * FROM movies")
        # THEORY · L4 · fetchall(): returns every result row (each a sqlite3.Row
        # thanks to the row_factory set in db.py).
        movies = cursor.fetchall()

    # THEORY · L4 · JSON response: returning a dict lets FastAPI serialise it to
    # `application/json` (the REST data-interchange format). dict(m) turns each
    # Row into a JSON object.
    return {"status": "success", "movies": [dict(m) for m in movies]}


# THEORY · L4 · Path parameter with a type annotation:
#   `{movie_id}` in the route is a PATH parameter; declaring `movie_id: int`
#   makes FastAPI parse and validate it as an integer (a non-numeric path
#   segment → automatic 422, no code of ours). This is the lecture's
#   "declare path parameters with curly brackets, type them with annotations."
@router.get("/ratings/{movie_id}")
def get_ratings(movie_id: int):
    """
    Return all ratings for a given movie.

    (Bug fix: the original queried a column named `movie_id`, but the schema
    column is `movieId`, so this endpoint used to raise an OperationalError.)
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ratings WHERE movieId = ?", (movie_id,))
        ratings = cursor.fetchall()

    return {"status": "success", "ratings": [dict(r) for r in ratings]}


# THEORY · L4 · POST + request body Create:
#   POST is the verb for sending data to create a resource. The `movie: MovieAdd`
#   parameter is a Pydantic model, so FastAPI reads the JSON body, validates it,
#   and hands us a typed object (see models.py). This is CRUD's "Create."
@router.post("/movies")
def add_movie(movie: MovieAdd):
    """
    Insert a new movie and return its id.

    `movieId` is declared INTEGER PRIMARY KEY, so SQLite auto-assigns the next
    free id (max rowid + 1) — guaranteeing a unique id as the spec requires.
    The response key is `movieId` to match the spec exactly.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO movies (title, genres) VALUES (?, ?)",
            (movie.title, movie.genres),
        )
        # THEORY · L4 · INSERT opens a transaction → commit() to persist it.
        conn.commit()
        # THEORY · L4 · cursor.lastrowid returns the auto-generated primary key
        # of the row just inserted — the new movie's unique id.
        movie_id = cursor.lastrowid

    return {"status": "success", "movieId": movie_id}
