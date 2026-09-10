"""Spring assignment: request-local ratings in, computed recommendations out."""

from fastapi import APIRouter

from models import RecommendationRequest
from recommender import recommend

router = APIRouter()


@router.post("/recommendations")
def get_recommendations(req: RecommendationRequest):
    # POST is specified for this structured input. REST statelessness means no
    # remembered client session, not "no database" or "no writes allowed".
    # Here the assignment separately requires that these ratings are not saved.
    input_ratings = [(r.movieId, r.rating) for r in req.ratings]
    return {"status": "success", "recommendations": recommend(input_ratings)}
