"""
Database access layer.

Single source of truth for:
  - where the SQLite file and dataset live (paths resolved relative to THIS
    file, so the backend works no matter which directory uvicorn is launched
    from), and
  - how the rest of the app opens a connection (`get_db`).

Keeping all path/connection logic here means the route modules never hard-code
"movielens.db" or worry about the current working directory.

────────────────────────────────────────────────────────────────────────────
THEORY · L4 Server-side/REST · SQLite
  SQLite is the embedded database from the lecture: a C library that software
  developers embed directly in their app (no separate DB server process). It
  follows PostgreSQL-ish SQL syntax but uses a DYNAMIC type system — it does
  not enforce column types by default (storage classes NULL / INTEGER / REAL /
  TEXT / BLOB). Python talks to it through the standard-library `sqlite3`
  module, which is a DB-API 2.0 driver — the Python equivalent of the JDBC API
  the Java half of the course used to reach a relational database.
────────────────────────────────────────────────────────────────────────────
"""

import os
import sqlite3
from contextlib import contextmanager

# The source code now lives in backend/src/, but the dataset zip and the
# generated SQLite file live one level up in backend/ (data kept separate from
# code). So we anchor data paths to the *parent* of this file's directory, which
# keeps the DB and dataset where they are regardless of where the server runs.
SRC_DIR = os.path.dirname(os.path.abspath(__file__))   # .../backend/src
BASE_DIR = os.path.dirname(SRC_DIR)                     # .../backend  (data + db live here)
DB_PATH = os.path.join(BASE_DIR, "movielens.db")


# THEORY · L4 · Open/Close a DB connection with the `with` statement:
#   The lecture stresses two things about a DB connection: you connect to an
#   existing DB (or create a new file — or ':memory:' for an in-memory one),
#   and "it's important to close the connection to free up resources." Python's
#   @contextmanager lets us package "open → hand out → always close" so callers
#   write `with get_db() as conn:` and the connection is guaranteed closed by
#   the `finally` block even if the body raises.
@contextmanager
def get_db():
    """
    Yield a SQLite connection and guarantee it is closed afterwards.

    `row_factory = sqlite3.Row` lets us treat rows like dicts (row["title"])
    and makes `dict(row)` produce clean JSON-ready objects for the responses.
    """
    conn = sqlite3.connect(DB_PATH)
    # THEORY · L4 · row representation: by default sqlite3 returns each row as a
    # plain tuple (positional). sqlite3.Row gives name-based access, so we can
    # do dict(row) and hand FastAPI a clean object it will serialise to JSON.
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
    # THEORY · L2/L4 · statelessness vs. persistence: HTTP itself is stateless,
    # but the application server keeps persistent state — here, the SQLite file.
    # This guard makes startup idempotent: build the DB only the first time.
    if os.path.exists(DB_PATH):
        return
    from setup_db import initialize_db

    initialize_db()
