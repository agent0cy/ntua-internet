"""
User-based collaborative filtering recommender.

Implements exactly the algorithm specified in the assignment:

  1. For the web-app user `u` (the ratings sent in the request), find the
     database users `v` who rated at least one of the same movies.
  2. similarity sim(u, v) = Pearson correlation computed over the items both
     u and v rated (the "co-rated" items).
  3. Keep the top-K most similar users  -> the neighbourhood N(u).
  4. For each candidate movie i that u has NOT rated, predict:

                       Σ_{v∈N(u)} sim(u,v) · (r_{v,i} − r̄_v)
         r̂_{u,i} = r̄_u + ──────────────────────────────────────
                              Σ_{v∈N(u)} |sim(u,v)|

  5. Return the top-N movies by predicted rating.

Implementation notes / design choices (documented because the assignment
requires being able to explain the code):

  * Pure Python, no numpy. The dataset is small (~100k ratings, 610 users) and
    the neighbourhood is tiny (K), so plain loops are fast and dependency-free.
  * For the Pearson similarity, the per-user means are taken over the *co-rated*
    items — the literal Pearson correlation of the two restricted rating vectors.
  * For the prediction formula, r̄_u is u's mean over the ratings it supplied,
    and r̄_v is neighbour v's mean over *all* the movies v rated in the DB.
  * Only neighbours with a positive correlation contribute (negative-correlation
    users disagree with u and would add noise).
  * Predicted ratings are clamped to the MovieLens [0.5, 5.0] scale for display.

────────────────────────────────────────────────────────────────────────────
THEORY · This module is the assignment's DOMAIN logic (the recommendation
algorithm), not a course HTTP/JS topic. Its course-relevant touch points are:
  o it runs only SELECT queries — read-only "stateless compute" feeding the
    POST /recommendations endpoint (REST stateless principle),
  o every query uses `?` PLACEHOLDERS built dynamically from the input list,
    so user-supplied movie ids are bound, never concatenated (SQL injection
    safety, L4), and
  o it opens the DB through the same `with get_db()` context manager, so the
    connection is always closed (L4 resource management).
────────────────────────────────────────────────────────────────────────────
"""

from math import sqrt

from db import get_db

# Tunable parameters. The assignment lets us pick K and N freely.
TOP_K = 30        # size of the neighbourhood N(u)
TOP_N = 10        # number of recommendations returned
MIN_COMMON = 2    # min co-rated movies for a meaningful Pearson value
MIN_SUPPORT = 3   # min neighbours who must have rated a candidate movie

# Why MIN_SUPPORT: without it, a single very-similar neighbour who rated an
# obscure film 5.0 produces an over-confident prediction (clamped to 5.0),
# flooding the results with niche titles backed by one opinion. Requiring a few
# neighbours to agree makes the top-N both more reliable and more recognisable.
# When fewer than MIN_SUPPORT neighbours exist, all available neighbours must
# support a candidate so the threshold does not make recommendations impossible.
# This is a standard CF "support" safeguard, not part of the core formula.


def _pearson(u_vals, v_vals):
    """
    Pearson correlation coefficient of two equal-length rating vectors.

    Returns 0.0 when either vector has zero variance (e.g. a user gave the same
    rating to every co-rated movie) — the correlation is undefined there, and 0
    correctly means "no usable signal".
    """
    n = len(u_vals)
    mean_u = sum(u_vals) / n
    mean_v = sum(v_vals) / n

    numerator = sum((a - mean_u) * (b - mean_v) for a, b in zip(u_vals, v_vals))
    denom = sqrt(sum((a - mean_u) ** 2 for a in u_vals)) * sqrt(
        sum((b - mean_v) ** 2 for b in v_vals)
    )
    if denom == 0:
        return 0.0
    return numerator / denom


# Widest possible gap between two ratings on the MovieLens 0.5–5.0 scale.
RATING_SPAN = 4.5


def _similarity(u_vals, v_vals):
    """
    Similarity between two aligned rating vectors over their co-rated items.

      * 2+ co-rated items -> Pearson correlation (the metric the spec asks for).
      * exactly 1 co-rated item -> Pearson is undefined (a single point has zero
        variance), so fall back to rating *closeness* on that one movie: 1.0 when
        both users gave it the same score, sliding to 0.0 at the maximum possible
        gap. This is what lets a user who rated only ONE movie still get
        recommendations instead of an empty list.
    """
    if len(u_vals) >= 2:
        return _pearson(u_vals, v_vals)
    return 1.0 - abs(u_vals[0] - v_vals[0]) / RATING_SPAN


def recommend(input_ratings):
    """
    `input_ratings`: list of (movieId, rating) supplied by the web-app user.
    Returns a list of recommendation dicts:
        {movieId, title, genres, predictedRating}
    sorted by predictedRating descending (at most TOP_N items).
    """
    input_dict = {movie_id: rating for movie_id, rating in input_ratings}
    if not input_dict:
        return []

    mean_u = sum(input_dict.values()) / len(input_dict)   # r̄_u
    movie_ids = list(input_dict.keys())

    with get_db() as conn:
        cursor = conn.cursor()

        # --- Step 1: users who overlap with u on at least one input movie -----
        # THEORY · L4 · dynamic parameterized query: we build one `?` per input
        # movie id ("?,?,?") and bind the ids as parameters — a safe SQL `IN`
        # list with no string interpolation of user data.
        placeholders = ",".join("?" for _ in movie_ids)
        cursor.execute(
            f"SELECT userId, movieId, rating FROM ratings "
            f"WHERE movieId IN ({placeholders})",
            movie_ids,
        )
        # corated[v] = {movieId: rating} restricted to u's input movies.
        corated = {}
        for row in cursor.fetchall():
            corated.setdefault(row["userId"], {})[row["movieId"]] = row["rating"]

        # --- Step 2: similarity on co-rated items -----------------------------
        # When u supplied only ONE rating, every neighbour shares at most that
        # one movie, so Pearson (needs >=2 points) is undefined for all of them.
        # In that case accept a single common movie and let _similarity fall back
        # to rating closeness, so the user still gets recommendations.
        solo = len(input_dict) == 1
        min_common = 1 if solo else MIN_COMMON

        similarities = {}
        for v, v_ratings in corated.items():
            common = [m for m in v_ratings if m in input_dict]
            if len(common) < min_common:
                continue
            sim = _similarity(
                [input_dict[m] for m in common],
                [v_ratings[m] for m in common],
            )
            if sim > 0:                       # keep only positively-correlated users
                similarities[v] = sim

        if not similarities:
            return []

        # --- Step 3: top-K neighbourhood N(u) ---------------------------------
        neighbours = sorted(
            similarities.items(), key=lambda kv: kv[1], reverse=True
        )[:TOP_K]
        neighbour_ids = [v for v, _ in neighbours]
        sim_of = dict(neighbours)

        # Fetch every rating of the neighbours: needed both for their global
        # mean r̄_v and to discover candidate movies to recommend.
        ph = ",".join("?" for _ in neighbour_ids)
        cursor.execute(
            f"SELECT userId, movieId, rating FROM ratings WHERE userId IN ({ph})",
            neighbour_ids,
        )
        neigh_ratings = {}
        for row in cursor.fetchall():
            neigh_ratings.setdefault(row["userId"], {})[row["movieId"]] = row["rating"]

        mean_v = {                            # r̄_v for each neighbour
            v: sum(rs.values()) / len(rs) for v, rs in neigh_ratings.items()
        }

        # --- Step 4: weighted prediction per candidate movie ------------------
        numerator = {}   # movieId -> Σ sim·(r_vi − r̄_v)
        denominator = {}  # movieId -> Σ |sim|
        support = {}      # movieId -> how many neighbours rated it
        for v in neighbour_ids:
            sim = sim_of[v]
            rv_mean = mean_v[v]
            for movie_id, rating in neigh_ratings[v].items():
                if movie_id in input_dict:
                    continue                  # skip movies u already rated
                numerator[movie_id] = numerator.get(movie_id, 0.0) + sim * (rating - rv_mean)
                denominator[movie_id] = denominator.get(movie_id, 0.0) + abs(sim)
                support[movie_id] = support.get(movie_id, 0) + 1

        required_support = min(MIN_SUPPORT, len(neighbour_ids))
        predictions = []
        for movie_id, num in numerator.items():
            den = denominator[movie_id]
            if den == 0 or support[movie_id] < required_support:
                continue
            predictions.append((movie_id, mean_u + num / den))

        # --- Step 5: top-N by predicted rating --------------------------------
        predictions.sort(key=lambda mp: mp[1], reverse=True)
        top = predictions[:TOP_N]
        if not top:
            return []

        # Attach title + genres in a single batched lookup, then re-order to
        # match the ranking (SQL IN does not preserve order).
        top_ids = [movie_id for movie_id, _ in top]
        ph2 = ",".join("?" for _ in top_ids)
        cursor.execute(
            f"SELECT movieId, title, genres FROM movies WHERE movieId IN ({ph2})",
            top_ids,
        )
        info = {row["movieId"]: row for row in cursor.fetchall()}

    results = []
    for movie_id, predicted in top:
        row = info.get(movie_id)
        results.append(
            {
                "movieId": movie_id,
                "title": row["title"] if row else "",
                "genres": row["genres"] if row else "",
                # clamp to the valid MovieLens scale and round for display
                "predictedRating": round(max(0.5, min(5.0, predicted)), 2),
            }
        )
    return results


if __name__ == "__main__":
    # ponytail: self-check for the similarity logic (no DB, no framework).
    assert abs(_pearson([1, 2, 3], [1, 2, 3]) - 1.0) < 1e-9   # perfect match -> +1
    assert abs(_pearson([1, 2, 3], [3, 2, 1]) + 1.0) < 1e-9   # perfect inverse -> -1
    assert _pearson([2, 2], [5, 1]) == 0.0                    # zero variance -> 0
    assert _similarity([4.0], [4.0]) == 1.0                   # identical single rating
    assert _similarity([0.5], [5.0]) == 0.0                   # widest single-rating gap
    assert 0.0 < _similarity([5.0], [4.0]) < 1.0              # close but not equal
    print("recommender self-check OK")
