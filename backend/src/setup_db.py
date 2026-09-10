"""Create the three CSV-shaped tables and import the bundled MovieLens data."""

import csv
import os
import sqlite3
import zipfile
import tempfile
from contextlib import closing

from db import BASE_DIR, DB_PATH

ZIP_PATH = os.path.join(BASE_DIR, "ml-latest-small.zip")
DATA_DIR = os.path.join(BASE_DIR, "ml-latest-small")

def _load_csv(filename, columns):
    """Read `columns` out of a CSV in the extracted dataset dir as tuples."""
    path = os.path.join(DATA_DIR, filename)
    with open(path, newline="", encoding="utf-8") as f:
        # CSV quoting handles commas inside titles; splitting on commas would fail.
        reader = csv.DictReader(f)
        return [tuple(row[col] for col in columns) for row in reader]

def initialize_db(replace=False):
    """Build once; explicit reset replaces the old file only after a full import.

    Run reset only with the backend stopped, so no connections use the old file.
    """
    if os.path.exists(DB_PATH) and not replace:
        print(f"Keeping existing database at {DB_PATH}")
        return

    if not os.path.isdir(DATA_DIR):
        with zipfile.ZipFile(ZIP_PATH, "r") as zf:
            zf.extractall(BASE_DIR)

    # CSV values are strings. Convert IDs, timestamps and ratings explicitly;
    # SQLite also has type affinity, so its storage is not simply "as passed".
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

    # Build beside the destination: a failed import never damages the live DB.
    fd, temporary_path = tempfile.mkstemp(suffix=".db", dir=BASE_DIR)
    os.close(fd)
    try:
        with closing(sqlite3.connect(temporary_path)) as conn, conn:
            # Explicit BEGIN includes DDL and inserts in one transaction.
            conn.execute("BEGIN")
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

            # with conn commits on success or rolls back on exception.
            # closing(conn) separately guarantees connection cleanup.
        os.replace(temporary_path, DB_PATH)
    finally:
        if os.path.exists(temporary_path):
            os.remove(temporary_path)

    print(
        f"Database created at {DB_PATH}: "
        f"{len(movies)} movies, {len(ratings)} ratings, {len(tags)} tags."
    )


if __name__ == "__main__":
    initialize_db()
