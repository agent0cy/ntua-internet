"""June 2026 extension: POST tag search with exact / five-character matching."""

# ---------- June 2026 extension starts ----------
from fastapi import APIRouter

from db import get_db
from models import TagMoviesRequest

router = APIRouter()


@router.post("/tags/movies")
def get_movies_for_tag(req: TagMoviesRequest):
    keyword = req.search
    # KEYWORD length selects the rule. Slice before casefold so we compare
    # the first five original characters, including Unicode text.
    if len(keyword) < 5:
        where_clause = "casefold(t.tag) = ?"
    else:
        where_clause = "casefold(substr(t.tag, 1, 5)) = ?"

    with get_db() as conn:
        # JOIN associates tags with movies; GROUP BY returns each movie once.
        # MIN selects one actual matching tag. Only fixed SQL is interpolated;
        # the user's keyword remains a bound parameter.
        movies = conn.execute(
            f"""
            SELECT m.movieId, m.title, m.genres, MIN(t.tag) AS matchingTag
            FROM tags AS t
            JOIN movies AS m ON m.movieId = t.movieId
            WHERE {where_clause}
            GROUP BY m.movieId, m.title, m.genres
            ORDER BY m.title, m.movieId
            """,
            (keyword[:5].casefold(),),
        ).fetchall()
    return {"status": "success", "movies": [dict(m) for m in movies]}
# ---------- June 2026 extension finishes ----------
