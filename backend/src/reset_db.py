"""Explicit reset: stop the backend first, then run python src/reset_db.py.

Replaces the database with the bundled dataset, removing added movies.
The existing file survives if creation or import fails.
"""

from setup_db import initialize_db


if __name__ == "__main__":
    initialize_db(replace=True)
