"""Run with backend/venv/bin/python -m unittest discover -s backend/tests -v.

Uses the real ASGI app and temporary SQLite files, without a test dependency
or changes to backend/movielens.db. HTTP parsing by Uvicorn is checked separately
when exercising the running application in a browser.
"""

import asyncio
import json
import math
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import quote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import db
import setup_db
from main import app
from recommender import _pearson, recommend, TOP_K


def request(method, url, body=None, headers=()):
    """Deliver a complete ASGI HTTP request and collect its response."""
    url = urlsplit(url)
    data = b"" if body is None else json.dumps(body).encode()
    scope = {
        "type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
        "method": method, "scheme": "http", "path": url.path,
        "raw_path": url.path.encode(), "query_string": url.query.encode(),
        "root_path": "", "server": ("localhost", 3000), "client": ("127.0.0.1", 1),
        "headers": [(b"content-type", b"application/json"), *headers],
    }
    messages = []

    async def receive():
        return {"type": "http.request", "body": data, "more_body": False}

    async def send(message):
        messages.append(message)

    asyncio.run(app(scope, receive, send))
    start = next(m for m in messages if m["type"] == "http.response.start")
    payload = b"".join(m.get("body", b"") for m in messages if m["type"] == "http.response.body")
    return start["status"], dict(start["headers"]), payload


class AppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.base = Path(cls.directory.name) / "base.db"
        # Extract and import into a temporary folder using the actual setup code.
        with patch.object(setup_db, "BASE_DIR", cls.directory.name), patch.object(setup_db, "DB_PATH", str(cls.base)), patch.object(setup_db, "DATA_DIR", str(Path(cls.directory.name) / "ml-latest-small")):
            setup_db.initialize_db()

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def setUp(self):
        self.path = str(Path(self.directory.name) / "test.db")
        shutil.copyfile(self.base, self.path)
        self.patch = patch.object(db, "DB_PATH", self.path)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def api(self, method, path, body=None):
        status, headers, payload = request(method, "/movielens/api" + path, body)
        self.assertIn(b"application/json", headers[b"content-type"])
        return status, json.loads(payload)

    def test_dataset_schema_counts_and_idempotent_setup(self):
        with db.get_db() as conn:
            for table, expected in [("movies", 9742), ("ratings", 100836), ("tags", 3683)]:
                self.assertEqual(conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0], expected)
            self.assertEqual([r[1] for r in conn.execute("PRAGMA table_info(tags)")], ["userId", "movieId", "tag", "timestamp"])
        before = Path(self.path).read_bytes()
        with patch.object(setup_db, "DB_PATH", self.path):
            setup_db.initialize_db()
        self.assertEqual(before, Path(self.path).read_bytes())

    def test_creation_search_literal_unicode_and_persistence(self):
        title = '<b>100%_ Ελληνική & Film</b>'
        status, result = self.api("POST", "/movies", {"title": "  " + title + "  ", "genres": "Drama"})
        self.assertEqual(status, 201)
        _, second = self.api("POST", "/movies", {"title": "Other", "genres": "Comedy"})
        self.assertNotEqual(result["movieId"], second["movieId"])
        for keyword in ["εΛΛΗΝΙΚΉ", "100%_", "& Film"]:
            status, found = self.api("GET", "/movies?search=" + quote(keyword))
            self.assertEqual(status, 200)
            self.assertEqual([m["title"] for m in found["movies"]], [title])
        self.assertEqual(self.api("GET", "/movies?search=" + quote("' OR 1=1 --"))[1]["movies"], [])
        self.assertEqual(len(self.api("GET", "/movies")[1]["movies"]), 9744)

    def test_ratings_and_validation(self):
        self.assertGreater(len(self.api("GET", "/ratings/1")[1]["ratings"]), 0)
        self.assertEqual(self.api("GET", "/ratings/999999")[1]["ratings"], [])
        for path in ["/ratings/nope", "/ratings/0"]:
            self.assertEqual(self.api("GET", path)[0], 422)
        for body in [{}, {"title": "  ", "genres": "Drama"}, {"title": "X", "genres": " "}]:
            self.assertEqual(self.api("POST", "/movies", body)[0], 422)
        for value in [0, 5.5, 4.3, "4.5", True, float("nan"), float("inf")]:
            self.assertEqual(self.api("POST", "/recommendations", {"ratings": [{"movieId": 1, "rating": value}]})[0], 422)
        for movie_id in [0, -1, "1", True]:
            self.assertEqual(self.api("POST", "/recommendations", {"ratings": [{"movieId": movie_id, "rating": 4.5}]})[0], 422)
        self.assertEqual(self.api("POST", "/recommendations", {"ratings": [{"movieId": 1, "rating": 4}, {"movieId": 1, "rating": 5}]})[0], 422)

    def test_tag_search_extension_is_absent(self):
        # The Spring assignment requires the tags table, but no tag-search API.
        for method in ("GET", "POST"):
            self.assertEqual(self.api(method, "/tags/movies", {"search": "funny"})[0], 404)

    def test_pearson_and_prediction_formula(self):
        self.assertAlmostEqual(_pearson([5, 1], [4, 2]), 1)
        self.assertAlmostEqual(_pearson([5, 1], [1, 5]), -1)
        for left, right in [([], []), ([5], [4]), ([4, 4], [1, 5])]:
            self.assertIsNone(_pearson(left, right))
        self.assertEqual(_pearson([1, 5, 3, 3], [3, 3, 1, 5]), 0)
        with db.get_db() as conn:
            conn.execute("DELETE FROM ratings")
            rows = [(1, 1, 5), (1, 2, 1), (1, 3, 5), (1, 4, 1), (2, 1, 1), (2, 2, 5), (2, 3, 1), (2, 5, 5), (3, 1, 4), (3, 2, 2), (3, 6, 5)]
            conn.executemany("INSERT INTO ratings VALUES (?, ?, ?, 0)", rows)
            conn.commit()
        # Hand calculation: sim = +1,-1,+1; means = 3,3,11/3; mean_u = 3.
        result = recommend([(1, 5), (2, 1)])
        self.assertEqual([(r["movieId"], r["predictedRating"]) for r in result], [(3, 5), (6, 4.33), (4, 1), (5, 1)])
        self.assertEqual(recommend([(1, 5), (2, 4)])[0]["predictedRating"], 6.5)

    def test_zero_correlation_neighbours_outrank_negative_ones(self):
        # Literal top-K: TOP_K users with a valid Pearson of exactly 0 fill N(u)
        # ahead of a negatively correlated user, and zero total weight means no prediction.
        with db.get_db() as conn:
            conn.execute("DELETE FROM ratings")
            rows = [(v, m, r) for v in range(1, TOP_K + 1) for m, r in [(1, 3), (2, 3), (3, 1), (4, 5), (5, 5)]]
            rows += [(TOP_K + 1, 1, 5), (TOP_K + 1, 2, 1), (TOP_K + 1, 6, 5)]
            conn.executemany("INSERT INTO ratings VALUES (?, ?, ?, 0)", rows)
            conn.commit()
        ratings = [(1, 1), (2, 5), (3, 3), (4, 3)]
        self.assertEqual(recommend(ratings), [])
        with db.get_db() as conn:
            conn.execute("DELETE FROM ratings WHERE userId = ?", (TOP_K,))
            conn.commit()
        # A free slot admits the sim -1 user: movie 6 predicts 3 - (5 - 11/3); movie 5 stays undefined.
        self.assertEqual([(r["movieId"], r["predictedRating"]) for r in recommend(ratings)], [(6, 1.67)])

    def test_empty_cold_start_and_request_ratings_not_saved(self):
        before = Path(self.path).read_bytes()
        for ratings in [[], [{"movieId": 1, "rating": 5}], [{"movieId": 1, "rating": 5}, {"movieId": 32, "rating": 5}], [{"movieId": 999999, "rating": 4}]]:
            status, data = self.api("POST", "/recommendations", {"ratings": ratings})
            self.assertEqual((status, data["recommendations"]), (200, []))
        status, data = self.api("POST", "/recommendations", {"ratings": [{"movieId": 1, "rating": 5}, {"movieId": 32, "rating": 2}]})
        self.assertEqual(status, 200)
        self.assertTrue(0 < len(data["recommendations"]) <= 10)
        self.assertTrue(all(math.isfinite(r["predictedRating"]) and r["movieId"] not in (1, 32) for r in data["recommendations"]))
        self.assertEqual(before, Path(self.path).read_bytes())

    def test_cors_preflight_and_openapi(self):
        status, headers, _ = request("OPTIONS", "/movielens/api/movies", headers=[(b"origin", b"http://localhost:8080"), (b"access-control-request-method", b"POST"), (b"access-control-request-headers", b"content-type")])
        self.assertEqual(status, 200)
        self.assertEqual(headers[b"access-control-allow-origin"], b"*")
        self.assertIn(b"POST", headers[b"access-control-allow-methods"])
        status, _, payload = request("GET", "/openapi.json")
        self.assertEqual(status, 200)
        paths = json.loads(payload)["paths"]
        self.assertEqual({path: set(operations) for path, operations in paths.items()}, {
            "/movielens/api/movies": {"get", "post"},
            "/movielens/api/ratings/{movie_id}": {"get"},
            "/movielens/api/recommendations": {"post"},
        })

    def test_failed_rebuild_preserves_database(self):
        before = Path(self.path).read_bytes()
        load_csv = setup_db._load_csv

        def duplicate_movie(filename, columns):
            rows = load_csv(filename, columns)
            return rows + [rows[0]] if filename == "movies.csv" else rows

        files_before = set(Path(self.directory.name).glob("*.db"))
        with patch.object(setup_db, "DB_PATH", self.path), patch.object(setup_db, "BASE_DIR", self.directory.name), patch.object(setup_db, "DATA_DIR", str(Path(self.directory.name) / "ml-latest-small")), patch.object(setup_db, "_load_csv", side_effect=duplicate_movie):
            # Fail during INSERT, after the temporary database and tables exist.
            with self.assertRaises(sqlite3.IntegrityError):
                setup_db.initialize_db(replace=True)
        self.assertEqual(before, Path(self.path).read_bytes())
        self.assertEqual(set(Path(self.directory.name).glob("*.db")), files_before)
        with db.get_db() as conn:
            self.assertEqual(conn.execute("PRAGMA integrity_check").fetchone()[0], "ok")


if __name__ == "__main__":
    unittest.main()
