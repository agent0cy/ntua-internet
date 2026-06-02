"""
Database creation + population script.

Reads the bundled MovieLens "latest-small" CSVs and loads them into an SQLite
database whose tables mirror the CSV structure (movies / ratings / tags).

Can be used two ways:
  - imported and called by the app on first startup (see db.init_database), or
  - run directly to (re)build the database:  `python setup_db.py`
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
        reader = csv.DictReader(f)
        return [tuple(row[col] for col in columns) for row in reader]


def initialize_db():
    # 1. Extract the dataset only if it hasn't been extracted yet.
    if not os.path.isdir(DATA_DIR):
        with zipfile.ZipFile(ZIP_PATH, "r") as zf:
            zf.extractall(BASE_DIR)

    # 2. Read the three CSVs. Values are cast to their target types so the
    #    stored data is unambiguous (movieId/userId as INTEGER, rating as REAL)
    #    rather than relying on SQLite column affinity to coerce strings.
    movies = [
        (int(mid), title, genres)
        for mid, title, genres in _load_csv("movies.csv", ["movieId", "title", "genres"])
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
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
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

        # executemany does a single batched, C-level insert per table — far
        # faster than inserting rows one-by-one for ~100k ratings.
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
        conn.commit()

    print(
        f"Database created at {DB_PATH}: "
        f"{len(movies)} movies, {len(ratings)} ratings, {len(tags)} tags."
    )


if __name__ == "__main__":
    initialize_db()
