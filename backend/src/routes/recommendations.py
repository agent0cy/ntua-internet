"""
Recommendation endpoint.

  POST /recommendations   personalized recommendations from session ratings

The collaborative-filtering logic lives in recommender.py; this module is just
the thin HTTP layer that validates the body and shapes the response.

────────────────────────────────────────────────────────────────────────────
THEORY · L1/L4 · REST "Stateless" principle
  Why POST and not GET? Because the request carries a structured body (a list
  of {movieId, rating} pairs), and bodies belong to POST/PUT/PATCH. Why is
  nothing saved? A core REST constraint is that the service is STATELESS —
  every request must carry all the data it needs, and the server keeps no
  client session between calls. This endpoint performs zero INSERTs: it reads
  the ratings, computes, and replies. It is "stateless compute."
────────────────────────────────────────────────────────────────────────────
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
    # THEORY · L4 · separation of concerns / Model-View-Controller flavour:
    #   this handler is the thin "controller" — it unpacks the validated
    #   Pydantic body into plain tuples and delegates the real work to the
    #   recommender "model" (recommender.py). Keeping HTTP plumbing and domain
    #   logic apart is the lecture's Model-2 (MVC) idea in miniature.
    input_ratings = [(r.movieId, r.rating) for r in req.ratings]
    recommendations = recommend(input_ratings)
    return {"status": "success", "recommendations": recommendations}
