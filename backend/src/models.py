"""Request schemas: FastAPI parses JSON into these Pydantic BaseModel objects.

Type hints alone do not validate ordinary Python functions. Pydantic performs
runtime checks here; invalid request data produces HTTP 422 before SQL runs.
These are validation models, not database tables or ORM models.
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MovieAdd(BaseModel):
    """Body for POST /movies; strip whitespace before checking required text."""

    model_config = ConfigDict(str_strip_whitespace=True)
    title: str = Field(min_length=1)
    genres: str = Field(min_length=1)


class RatingInput(BaseModel):
    """One MovieLens rating: positive ID and a half-star value from 0.5 to 5."""

    movieId: int = Field(gt=0, strict=True)
    rating: float = Field(ge=0.5, le=5, multiple_of=0.5, allow_inf_nan=False, strict=True)


class RecommendationRequest(BaseModel):
    """Nested models validate every item; an empty list legitimately gives []."""

    ratings: list[RatingInput]

    @field_validator("ratings")
    @classmethod
    def unique_movies(cls, ratings):
        # Silently keeping the last duplicate would hide ambiguous input.
        if len({r.movieId for r in ratings}) != len(ratings):
            raise ValueError("Each movieId must appear only once")
        return ratings


# ---------- June 2026 extension starts ----------
class TagMoviesRequest(BaseModel):
    """Body for POST /tags/movies; blank searches are not useful keywords."""

    model_config = ConfigDict(str_strip_whitespace=True)
    search: str = Field(min_length=1)
# ---------- June 2026 extension finishes ----------
