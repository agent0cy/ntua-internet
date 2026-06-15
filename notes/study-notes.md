# MovieLens Exam Study Notes

## DB Layer

**Files:** `setup_db.py` (builds/populates DB from CSVs) · `db.py` (paths + `get_db()` + first-run guard)
**Source:** `ml-latest-small.zip` — uses `movies/ratings/tags.csv` only.

**Schema (mirrors CSVs):**
- `movies(movieId PK, title, genres)` — genres = pipe-separated string
- `ratings(userId, movieId, rating, timestamp)` — PK `(userId, movieId)`
- `tags(userId, movieId, tag, timestamp)` — PK `(userId, movieId, tag)`

**ETL pipeline** (`initialize_db()`): `zip → unzip → csv.DictReader → cast types → executemany`
1. Unzip only if folder missing (idempotent)
2. `DictReader` reads header + rows as dicts
3. Cast strings → `int`/`float` (CSV gives all strings)
4. `CREATE TABLE IF NOT EXISTS` + batched `executemany` with `?` placeholders + `commit`

**Why-questions:**
- `csv.DictReader` not `split(",")` → titles contain commas (`"American President, The"`)
- `with sqlite3.connect()` = transaction (commit/rollback, no close); `get_db()` adds `try/finally: close()`
- `row_factory = sqlite3.Row` → `dict(row)` → JSON-ready responses

**Idempotency contract:** `db.init_database()` does `if os.path.exists(DB_PATH): return` → builds only on first run. `setup_db.py` uses plain `INSERT` (assumes fresh DB).

**Gotcha — rerun `setup_db.py` on existing DB:** table not recreated; plain `INSERT` of existing `movieId` → `IntegrityError` (rolls back) → **crashes**, no double data. Clean rebuild = `rm movielens.db && python setup_db.py`.
- `INSERT` = fail · `INSERT OR IGNORE` = skip · `INSERT OR REPLACE` = overwrite

## Recommendation System — Quick Notes

**What:** user-based collaborative filtering. "Find users with your taste, recommend what they loved." Uses only rating patterns, not genres.

**Files:** `recommender.py` (algorithm) · `routes/recommendations.py` (thin HTTP layer) · `index.js getRecommendations()` (frontend).

**The 5 steps** (`recommend()`):
1. SELECT DB users who rated ≥1 of your input movies (`:88-98`)
2. `sim(u,v)` = Pearson on co-rated items; keep `sim>0` and `≥MIN_COMMON` co-rated (`:100-114`)
3. Sort by sim, take top-`K` neighbours; fetch their ratings, compute each `mean_v` (`:116-136`)
4. Per unseen movie: `numerator += sim·(rating−mean_v)`, `denominator += |sim|`, `support += 1` (`:138-150`)
5. Keep `support≥MIN_SUPPORT`; `predicted = mean_u + num/den`; clamp `[0.5,5.0]`; sort desc, top-`N` (`:152-187`)

**Two formulas:**
- Pearson: `Σ(rᵤ−r̄ᵤ)(rᵥ−r̄ᵥ) / (√Σ(rᵤ−r̄ᵤ)² · √Σ(rᵥ−r̄ᵥ)²)` — range [−1,1]. Mean-centering cancels harsh-vs-generous users; measures *shape* of taste.
- Prediction: `r̂ = r̄ᵤ + Σ sim·(rᵥᵢ−r̄ᵥ) / Σ|sim|` — start from your mean, nudge by neighbours' deviations weighted by similarity.

**Two different means:** `r̄ᵤ` = mean of *your input* ratings; `r̄ᵥ` (in prediction) = neighbour's mean over *all* their DB ratings; Pearson's internal means = over co-rated only.

**Tunables** (`:38-41`): `TOP_K=30` (neighbourhood) · `TOP_N=10` (recs) · `MIN_COMMON=2` (Pearson needs ≥2 points) · `MIN_SUPPORT=3` (≥3 neighbours must rate a candidate — not in spec, anti-noise safeguard).

**Why-questions:**
- Why POST not GET? request carries a structured body (list of ratings).
- Why not stored? spec says session-only; route does **zero INSERTs**, recommender only SELECTs → "stateless compute".
- Why `|sim|` in denominator but signed in numerator? denominator normalizes (weighted avg); sign in numerator = direction. With positive-only filter `|sim|==sim` here, but keeps formula correct if anti-correlated neighbours allowed.
- Why all recs show 5.0? predictions exceed 5.0 and get **clamped** (cosmetic); true ranking still differs pre-clamp.

**Edge cases → empty `[]`:** no input ratings (`:79`, also frontend guard `index.js:159`) · no overlapping users · no neighbour with `sim>0` (`:113`).

**Single co-rated movie can never be a neighbour:** `MIN_COMMON=2` blocks it; even past that, 1 point → zero variance → Pearson returns 0 → fails `sim>0`.

**Tuning/PCA?** Not needed (spec lets you pick K,N). PCA belongs to *model-based* CF (matrix factorization), a different algorithm. To tune: hold-out split + RMSE + grid-search K.
