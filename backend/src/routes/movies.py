"""Spring assignment: title search, dataset ratings, and movie creation."""

from fastapi import APIRouter, Path

from db import get_db
from models import MovieAdd

router = APIRouter()


@router.get("/movies")
def search_movies(search: str = ""):
    """Query parameter: ?search=keyword; an empty keyword matches every title."""
    # Bound values prevent SQL injection. instr() treats % and _ literally,
    # unlike LIKE. casefold() also handles non-ASCII movie titles.
    with get_db() as conn:
        movies = conn.execute(
            "SELECT * FROM movies WHERE instr(casefold(title), ?) > 0 ORDER BY movieId",
            (search.casefold(),),
        ).fetchall()
    return {"status": "success", "movies": [dict(m) for m in movies]}


@router.get("/ratings/{movie_id}")
def get_ratings(movie_id: int = Path(gt=0)):
    """Path parameter: the ID belongs in the URL, not a JSON request body.

    No dataset ratings for this ID means an empty list. The frontend computes
    the mean, independently of the user's local ratings.
    """
    with get_db() as conn:
        ratings = conn.execute(
            "SELECT * FROM ratings WHERE movieId = ? ORDER BY userId", (movie_id,)
        ).fetchall()
    return {"status": "success", "ratings": [dict(r) for r in ratings]}


@router.post("/movies", status_code=201)
def add_movie(movie: MovieAdd):
    """Pydantic model parameter: FastAPI reads and validates the JSON body."""
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO movies (title, genres) VALUES (?, ?)",
            (movie.title, movie.genres),
        )
        # INTEGER PRIMARY KEY assigns a unique ID. Commit persists the row
        # across browser refreshes and backend restarts.
        conn.commit()
        movie_id = cursor.lastrowid
    return {"status": "success", "movieId": movie_id}
