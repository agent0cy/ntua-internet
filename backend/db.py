"""
Database access layer.

Single source of truth for:
  - where the SQLite file and dataset live (paths resolved relative to THIS
    file, so the backend works no matter which directory uvicorn is launched
    from), and
  - how the rest of the app opens a connection (`get_db`).

Keeping all path/connection logic here means the route modules never hard-code
"movielens.db" or worry about the current working directory.
"""

import os
import sqlite3
from contextlib import contextmanager

# Absolute directory of the backend package. Everything is anchored to this so
# that `python main.py`, `uvicorn main:app` from backend/, or `uvicorn
# backend.main:app` from the repo root all find the same files.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "movielens.db")


@contextmanager
def get_db():
    """
    Yield a SQLite connection and guarantee it is closed afterwards.

    `row_factory = sqlite3.Row` lets us treat rows like dicts (row["title"])
    and makes `dict(row)` produce clean JSON-ready objects for the responses.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """
    Create and populate the database on first run only (idempotent).

    The heavy import of `setup_db` is done lazily inside the function instead of
    at module top-level, because `setup_db` imports the path constants from this
    module — importing it at the top would create a circular import.
    """
    if os.path.exists(DB_PATH):
        return
    from setup_db import initialize_db

    initialize_db()
