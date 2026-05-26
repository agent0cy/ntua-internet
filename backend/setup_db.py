import zipfile, csv
import os, sqlite3


def initialize_db():
    with zipfile.ZipFile("ml-latest-small.zip", "r") as zf:
        zf.extractall(".")

    movies = []
    ratings = []
    tags = []

    with open("ml-latest-small/movies.csv", "r") as f:
        reader = csv.DictReader(f)
        movies = [(row["movieId"], row["title"], row["genres"]) for row in reader]

    with open("ml-latest-small/ratings.csv", "r") as f:
        reader = csv.DictReader(f)
        ratings = [(row["userId"], row["movieId"], row["rating"], row["timestamp"]) for row in reader]

    with open("ml-latest-small/tags.csv", "r") as f:
        reader = csv.DictReader(f)
        tags = [(row["userId"], row["movieId"], row["tag"], row["timestamp"]) for row in reader]
        
    # Initialize database and insert data
    with sqlite3.connect("movielens.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                movieId INTEGER PRIMARY KEY,
                title TEXT,
                genres TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                userId INTEGER,
                movieId INTEGER,
                rating REAL,
                timestamp INTEGER,
                PRIMARY KEY (userId, movieId)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                userId INTEGER,
                movieId INTEGER,
                tag TEXT,
                timestamp INTEGER,
                PRIMARY KEY (userId, movieId, tag)
            )
        """)
        
        # Better than inserting one by one, we can use executemany for batch insertion 
        # This is much faster than inserting rows one by one, especially for large datasets, as it reduces the number of round-trips to the database.
        # It also uses C-level optimizations in the SQLite library, making it more efficient for bulk inserts.
        cursor.executemany("INSERT INTO movies (movieId, title, genres) VALUES (?, ?, ?)", movies)
        cursor.executemany("INSERT INTO ratings (userId, movieId, rating, timestamp) VALUES (?, ?, ?, ?)", ratings)
        cursor.executemany("INSERT INTO tags (userId, movieId, tag, timestamp) VALUES (?, ?, ?, ?)", tags)
        
        conn.commit()
