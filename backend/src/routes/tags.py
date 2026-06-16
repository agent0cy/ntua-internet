"""
Tag search endpoint.

  POST /tags/movies   movies with at least one matching user-provided tag
"""

# ---------- tag search route module starts ----------
from fastapi import APIRouter

from db import get_db
from models import TagMoviesRequest

router = APIRouter()
# ---------- tag search route module finishes ----------

# --- EXAM Q ---
# ---------- tag-based movie search starts ----------
@router.post("/tags/movies")
def get_movies_for_tag(req: TagMoviesRequest):
    """Return movies whose tags match the requested keyword by assignment rules."""
    keyword = req.search.strip()

    # tag length matching rules:
    # - if the tag is less than 5 characters, match the entire tag
    # - if the tag is 5 or more characters, match only the first 5 characters
    if len(keyword) < 5:
        where_clause = "LOWER(t.tag) = LOWER(?)"
        params = (keyword,)
    else:
        where_clause = "LOWER(SUBSTR(t.tag, 1, 5)) = LOWER(?)"
        params = (keyword[:5],)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT
                m.movieId,
                m.title,
                m.genres,
                MIN(t.tag) AS matchingTag
            FROM tags AS t
            JOIN movies AS m ON m.movieId = t.movieId
            WHERE {where_clause}
            GROUP BY m.movieId, m.title, m.genres
            ORDER BY m.title
            """,
            params,
        )
        movies = cursor.fetchall()

    return {"status": "success", "movies": [dict(movie) for movie in movies]}
# ---------- tag-based movie search finishes ----------
