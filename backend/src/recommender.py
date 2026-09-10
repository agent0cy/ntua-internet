"""User-based collaborative filtering, following Spring assignment p.3.

1. Find users with co-rated movies.
2. Pearson similarity uses the means over those co-rated items only.
3. Select the top K=30 defined similarities, including zero and negative ones.
4. Predict unseen items: mean_u + sum(sim * (rating_vi - mean_v)) / sum(abs(sim)).
   Here mean_u uses all submitted ratings; mean_v uses all the neighbour's
   dataset ratings. For each candidate, only neighbours who rated it contribute
   to BOTH sums (missing ratings are not zero).
5. Rank scores and return at most N=10 movies. No extra support filter or clamp.

Empty input, insufficient overlap or zero variance can give no recommendations.
Submitted ratings are never written. Results also depend on the database, so
this read-only function is not a pure function of its request body alone.
"""

from math import sqrt

from db import get_db

# Tunable parameters. The assignment lets us pick K and N freely.
TOP_K = 30        # size of the neighbourhood N(u)
TOP_N = 10        # number of recommendations returned
MIN_COMMON = 2    # min co-rated movies for a meaningful Pearson value


def _pearson(u_vals, v_vals):
    """
    Pearson correlation coefficient of two equal-length rating vectors.

    Returns None for insufficient overlap or when a vector has zero variance (e.g.
    identical ratings on all co-rated movies): Pearson is undefined there. A
    genuine 0.0 is a valid result and must stay distinct from "undefined".
    """
    n = len(u_vals)
    if n < MIN_COMMON or n != len(v_vals):
        return None
    mean_u = sum(u_vals) / n
    mean_v = sum(v_vals) / n

    numerator = sum((a - mean_u) * (b - mean_v) for a, b in zip(u_vals, v_vals))
    denom = sqrt(sum((a - mean_u) ** 2 for a in u_vals)) * sqrt(
        sum((b - mean_v) ** 2 for b in v_vals)
    )
    if denom == 0:
        return None
    return numerator / denom


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

        # --- Step 2: Pearson similarity on co-rated items ---------------------
        similarities = {}
        for v, v_ratings in corated.items():
            common = [m for m in v_ratings if m in input_dict]
            if len(common) < MIN_COMMON:
                continue
            sim = _pearson(
                [input_dict[m] for m in common],
                [v_ratings[m] for m in common],
            )
            if sim is not None:               # keep 0.0: it outranks negatives in top-K
                similarities[v] = sim

        if not similarities:
            return []

        # --- Step 3: top-K neighbourhood N(u) ---------------------------------
        neighbours = sorted(
            similarities.items(), key=lambda kv: (-kv[1], kv[0])
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
        for v in neighbour_ids:
            sim = sim_of[v]
            rv_mean = mean_v[v]
            for movie_id, rating in neigh_ratings[v].items():
                if movie_id in input_dict:
                    continue                  # skip movies u already rated
                numerator[movie_id] = numerator.get(movie_id, 0.0) + sim * (rating - rv_mean)
                denominator[movie_id] = denominator.get(movie_id, 0.0) + abs(sim)

        predictions = []
        for movie_id, num in numerator.items():
            den = denominator[movie_id]
            if den == 0:
                continue                  # only zero-weight neighbours: undefined
            predictions.append((movie_id, mean_u + num / den))

        # --- Step 5: top-N by predicted rating --------------------------------
        predictions.sort(key=lambda mp: (-mp[1], mp[0]))
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
                # This is a prediction, not an input rating: the formula can
                # exceed [0.5, 5]. Rank raw scores, then round for display.
                "predictedRating": round(predicted, 2),
            }
        )
    return results
