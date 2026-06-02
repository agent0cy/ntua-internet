"""
Pydantic request models.

Typed models give us automatic request validation and self-documenting schemas
in the interactive docs (/docs). They also fix the original bug where the
recommendation body was typed as a bare `List[dict]` with no field validation.
"""

from typing import List

from pydantic import BaseModel


class MovieAdd(BaseModel):
    """Body for POST /movies."""

    title: str
    genres: str


class RatingInput(BaseModel):
    """A single {movieId, rating} pair inside a recommendation request."""

    movieId: int
    rating: float


class RecommendationRequest(BaseModel):
    """Body for POST /recommendations: the ratings the user gave this session."""

    ratings: List[RatingInput]
