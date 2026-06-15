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
