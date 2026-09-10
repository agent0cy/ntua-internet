"""One place for database paths and connection lifetime management."""

import os
import sqlite3
from contextlib import contextmanager

# Paths relative to this file work regardless of the launch directory.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "movielens.db")


@contextmanager
def get_db():
    """Open one connection per operation and always close it, even on errors.

    Callers explicitly commit successful writes. SQLite's own `with conn:`
    commits/rolls back, but does not close conn.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.create_function("casefold", 1, str.casefold, deterministic=True)
    conn.row_factory = sqlite3.Row  # Named columns; dict(row) is JSON-ready.
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """Initialize once; keep existing data on subsequent application starts."""
    if not os.path.exists(DB_PATH):
        # setup_db imports our paths; this local import avoids an import cycle.
        from setup_db import initialize_db

        initialize_db()
