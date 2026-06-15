"""
Movie + ratings endpoints.

  GET  /movies?search={keyword}   search movies by title (case-insensitive)
  GET  /ratings/{movieId}         all ratings for a movie
  POST /movies                    add a new movie

These are mounted under the `/movielens/api` prefix in main.py, so the full
paths are e.g. GET /movielens/api/movies.
"""

from typing import Optional

from fastapi import APIRouter

from db import get_db
from models import MovieAdd

router = APIRouter()


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
            cursor.execute(
                "SELECT * FROM movies WHERE title LIKE ?", (f"%{search}%",)
            )
        else:
            cursor.execute("SELECT * FROM movies")
        movies = cursor.fetchall()

    return {"status": "success", "movies": [dict(m) for m in movies]}


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
        conn.commit()
        movie_id = cursor.lastrowid

    return {"status": "success", "movieId": movie_id}
