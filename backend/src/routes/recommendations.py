"""
Recommendation endpoint.

  POST /recommendations   personalized recommendations from session ratings

The collaborative-filtering logic lives in recommender.py; this module is just
the thin HTTP layer that validates the body and shapes the response.
"""

from fastapi import APIRouter

from models import RecommendationRequest
from recommender import recommend

router = APIRouter()


@router.post("/recommendations")
def get_recommendations(req: RecommendationRequest):
    """
    Compute recommendations from the ratings the user provides. Per the spec,
    these ratings are used only for this request and are never stored.
    """
    input_ratings = [(r.movieId, r.rating) for r in req.ratings]
    recommendations = recommend(input_ratings)
    return {"status": "success", "recommendations": recommendations}
