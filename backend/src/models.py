"""
Pydantic request models.

Typed models give us automatic request validation and self-documenting schemas
in the interactive docs (/docs). They also fix the original bug where the
recommendation body was typed as a bare `List[dict]` with no field validation.

────────────────────────────────────────────────────────────────────────────
THEORY · L4 Server-side/REST · Request Body & Data Validation (Pydantic)
  The lecture's "Request Body and Data Validation" slide: to declare a request
  body in FastAPI you use a Pydantic model. For every incoming request FastAPI
  then automatically:
    o reads the body of the request as JSON,
    o makes the necessary data-type conversions (e.g. "5" → 5),
    o validates the data (wrong/missing fields → 422 error, no code of ours),
    o hands the parsed object to our function parameter, and
    o generates a JSON Schema for the model (part of the OpenAPI/Swagger docs).
  Each class below is one such schema. The `field: type` lines are standard
  Python type annotations — the same mechanism FastAPI reuses for path and
  query parameters.
────────────────────────────────────────────────────────────────────────────
"""

from typing import List

from pydantic import BaseModel


class MovieAdd(BaseModel):
    """Body for POST /movies."""

    # THEORY · L4 · JSON ↔ typed object: these two declared string fields are
    # exactly the name/value pairs the JSON request body must contain. Anything
    # else is rejected before our endpoint code ever runs.
    title: str
    genres: str


class RatingInput(BaseModel):
    """A single {movieId, rating} pair inside a recommendation request."""

    # THEORY · L4 · nested models: a Pydantic model may be used as the type of
    # another model's field (see RecommendationRequest below), so JSON objects
    # nested inside arrays are validated recursively.
    movieId: int
    rating: float


class RecommendationRequest(BaseModel):
    """Body for POST /recommendations: the ratings the user gave this session."""

    # THEORY · L4 · JSON arrays of objects: `List[RatingInput]` validates a JSON
    # array where each element must match the RatingInput schema. This is the
    # typed replacement for the original, unvalidated `List[dict]`.
    ratings: List[RatingInput]

# --- EXAM Q ---
# ---------- tag search request model starts ----------
class TagMoviesRequest(BaseModel):
    """Body for POST /tags/movies: the tag search text supplied by the user."""

    search: str
# ---------- tag search request model finishes ----------
