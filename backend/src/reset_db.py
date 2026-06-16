"""
Reset the SQLite database to a pristine state.

Deletes the current movielens.db and rebuilds it from the bundled dataset, so
you can restore clean data on demand (e.g. before a demo, or after adding test
movies). The app's normal startup is unaffected — this is a manual tool.

Run from backend/:  python src/reset_db.py

THEORY · L4 · idempotent rebuild: setup_db.py uses plain INSERTs and assumes a
fresh database, so re-running it against an existing DB would raise an
IntegrityError on the duplicate primary keys. Deleting the file first guarantees
a clean slate — the simplest "DROP everything and recreate" workflow.
"""

import os

from db import DB_PATH
from setup_db import initialize_db


def reset_db():
    """Delete the existing database file (if any), then rebuild from scratch."""
    try:
        os.remove(DB_PATH)
    except FileNotFoundError:
        pass

    initialize_db()


if __name__ == "__main__":
    reset_db()
