"""
Database creation + population script.

Reads the bundled MovieLens "latest-small" CSVs and loads them into an SQLite
database whose tables mirror the CSV structure (movies / ratings / tags).

Can be used two ways:
  - imported and called by the app on first startup (see db.init_database), or
  - run directly to (re)build the database on demand:  `python setup_db.py`

────────────────────────────────────────────────────────────────────────────
THEORY · L4 Server-side/REST · SQLite from Python (sqlite3)
  This file exercises the whole SQLite workflow the lecture walks through:
    o connect with the `with` statement,
    o a cursor "executes SQL commands and queries",
    o CREATE TABLE = DDL (Data Definition Language) declaring the schema,
    o INSERT with `?` PLACEHOLDERS = parameterized queries to avoid SQL
      injection,
    o executemany() to insert many rows from a list of tuples, and
    o commit() because "the INSERT statement implicitly opens a transaction,
      which needs to be committed before changes are saved."
────────────────────────────────────────────────────────────────────────────
"""

import csv
import os
import sqlite3
import zipfile

# Reuse the canonical paths so the DB is always created in the same place the
# app reads it from. (db.py only defines constants at import time, so importing
# it here is safe and does not trigger a circular import.)
from db import BASE_DIR, DB_PATH

ZIP_PATH = os.path.join(BASE_DIR, "ml-latest-small.zip")
DATA_DIR = os.path.join(BASE_DIR, "ml-latest-small")

def _load_csv(filename, columns):
    """Read `columns` out of a CSV in the extracted dataset dir as tuples."""
    path = os.path.join(DATA_DIR, filename)
    with open(path, newline="", encoding="utf-8") as f:
        # THEORY · data exchange formats: CSV is the simplest tabular text
        # format. csv.DictReader reads the header row and yields each data row
        # as a dict keyed by column name. We use it instead of str.split(",")
        # precisely because some titles contain commas
        # ("American President, The (1995)") which a naive split would corrupt.
        reader = csv.DictReader(f)
        return [tuple(row[col] for col in columns) for row in reader]

# 4 stage pipeline data extraction, transformation and loading into sqlite
# unzip -> read csvs with DictReader -> transform to typed tuples -> load into sqlite
def initialize_db():
    # 1. Extract the dataset only if it hasn't been extracted yet.
    if not os.path.isdir(DATA_DIR):
        with zipfile.ZipFile(ZIP_PATH, "r") as zf:
            zf.extractall(BASE_DIR)

    # 2. Read the three CSVs. Values are cast to their target types so the
    #    stored data is unambiguous (movieId/userId as INTEGER, rating as REAL)
    #    rather than relying on SQLite column affinity to coerce strings.
    #    in cases a variable is not casted, it is stored as TEXT in the database; in those cases, that's what we want (store a string e.g. title, genres, tag).
    # THEORY · L4 · SQLite dynamic typing & storage classes: CSV gives every
    # field as a string. Because SQLite does NOT enforce column types, whatever
    # Python type we pass is stored as-is. We therefore cast on purpose: int()
    # → INTEGER storage class, float() → REAL, leave-as-str → TEXT. This is the
    # manual version of the lecture's "adapter" idea (mapping Python types onto
    # SQLite values).
    movies = [
        (int(mid), title, genres)
        for mid, title, genres in _load_csv("movies.csv",
                                            ["movieId", "title", "genres"])
    ]
    ratings = [
        (int(uid), int(mid), float(rating), int(ts))
        for uid, mid, rating, ts in _load_csv(
            "ratings.csv", ["userId", "movieId", "rating", "timestamp"]
        )
    ]
    tags = [
        (int(uid), int(mid), tag, int(ts))
        for uid, mid, tag, ts in _load_csv(
            "tags.csv", ["userId", "movieId", "tag", "timestamp"]
        )
    ]

    # 3. Create the schema and bulk-insert. `with sqlite3.connect(...)` commits
    #    on success / rolls back on error automatically.
    # Create all tables first
    # THEORY · L4 · transactions via `with`: using the connection as a context
    # manager wraps the block in ONE transaction — it auto-commits if the block
    # succeeds and auto-rolls-back if it raises. So either all three tables are
    # filled, or (on error) the DB is left untouched. Atomicity for free.
    with sqlite3.connect(DB_PATH) as conn:
        # THEORY · L4 · cursor: the object that actually runs SQL against the DB.
        cursor = conn.cursor()
        # THEORY · L4 · DDL (CREATE TABLE): defines the schema. The columns
        # mirror the CSVs. `INTEGER PRIMARY KEY` makes movieId the rowid alias
        # so SQLite auto-assigns ids; the composite PRIMARY KEYs on ratings and
        # tags enforce "one rating per (user, movie)" / one tag per triple.
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS movies (
                movieId INTEGER PRIMARY KEY,
                title   TEXT,
                genres  TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ratings (
                userId    INTEGER,
                movieId   INTEGER,
                rating    REAL,
                timestamp INTEGER,
                PRIMARY KEY (userId, movieId)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tags (
                userId    INTEGER,
                movieId   INTEGER,
                tag       TEXT,
                timestamp INTEGER,
                PRIMARY KEY (userId, movieId, tag)
            )
            """
        )

        # then add all the data.
        # executemany does a single batched, C-level insert per table — far
        # faster than inserting rows one-by-one for ~100k ratings.
        # THEORY · L4 · executemany() + parameterized queries: the lecture's
        # exact recipe for "Insert Multiple Records" — pass the INSERT template
        # plus a list of tuples. The `?` are placeholders: values are bound by
        # the driver, never string-concatenated, which is what prevents SQL
        # injection.
        cursor.executemany(
            "INSERT INTO movies (movieId, title, genres) VALUES (?, ?, ?)", movies
        )
        cursor.executemany(
            "INSERT INTO ratings (userId, movieId, rating, timestamp) VALUES (?, ?, ?, ?)",
            ratings,
        )
        cursor.executemany(
            "INSERT INTO tags (userId, movieId, tag, timestamp) VALUES (?, ?, ?, ?)",
            tags,
        )

        # commit the transaction to save the changes to the database
        # do not close the connection here; the context manager will handle it automatically when exiting the block
        # THEORY · L4 · commit(): persists the transaction. (Here it is also
        # implied by the `with` block exiting cleanly, but committing
        # explicitly documents intent.)
        conn.commit()

    print(
        f"Database created at {DB_PATH}: "
        f"{len(movies)} movies, {len(ratings)} ratings, {len(tags)} tags."
    )


if __name__ == "__main__":
    initialize_db()
