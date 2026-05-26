"""
MovieLens Backend - FastAPI Backend
 
Endpoints:
  GET  /movielens/api/movies?search={keyword}       — search movies by title
  GET  /movielens/api/ratings/{movieId}             — get ratings for a movie
  POST /movielens/api/movies                        — add a new movie
  POST /movielens/api/recommendations               — get personalized recommendations
"""

import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from typing import Optional
from contextlib import asynccontextmanager, contextmanager
import os
from setup_db import initialize_db

import numpy as np

@asynccontextmanager
async def lifespan(app: FastAPI):
    # runs on startup
    print("Starting up...")
    if not os.path.exists("movielens.db"):
        print("Initializing database...")
        initialize_db()
    yield
    # runs on shutdown
    print("Shutting down...")

app = FastAPI(title="MovieLens Backend", lifespan=lifespan)

@contextmanager
def get_db():
    conn = sqlite3.connect("movielens.db")
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    try:
        yield conn
    finally:
        conn.close()

# ------------------------
# CORS Middleware
# ------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------
# define pydantic models
# ------------------------
class MovieAdd(BaseModel):
    title: str
    genres: str

class RecommendationRequest(BaseModel):
    ratings: List[dict]  # List of {"movieId": int, "rating": float}

# ------------------------
# API Endpoints
# ------------------------
@app.get("/movies")
def get_movies(search: Optional[str] = None):
    """Search movies by title"""
    with get_db() as conn:
        cursor = conn.cursor()
        if search:
            cursor.execute("SELECT * FROM movies WHERE title LIKE ?", (f"%{search}%",))
        else:
            cursor.execute("SELECT * FROM movies")
        movies = cursor.fetchall()
        
    return {"status": "success", "movies": [dict(movie) for movie in movies]}

@app.get("/ratings/{movie_id}")
def get_ratings(movie_id: int):
    """Get ratings for a movie"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ratings WHERE movie_id = ?", (movie_id,))
        ratings = cursor.fetchall()
        
    return {"status": "success", "ratings": [dict(rating) for rating in ratings]}

@app.post("/movies")
def add_movie(movie: MovieAdd):
    """Add a new movie"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO movies (title, genres) VALUES (?, ?)", (movie.title, movie.genres))
        conn.commit()
        movie_id = cursor.lastrowid
        
    return {"status": "success", "movie_id": movie_id}

@app.post("/recommendations")
def get_recommendations(req: RecommendationRequest):
    """Get personalized recommendations given the ratings that the user provides"""
    
    # 0. Store input ratings for user u
    input_ratings_dict = {r["movieId"]: r["rating"] for r in req.ratings}  # dict {"movieId": int, "rating": float}
    user_ratings_dict = {}   # list of (userId, movieId, rating) for users who rated the same movies as the input ratings
    
    # 1. Find users with overlapping rated movies
    with get_db() as conn:
        cursor = conn.cursor()
        movie_ids = [r["movieId"] for r in req.ratings]
        placeholders = ",".join("?" for _ in movie_ids)
        cursor.execute(f"""
            SELECT userId, movieId, rating 
            FROM ratings 
            WHERE movieId IN ({placeholders})
        """, movie_ids)
        user_ratings = cursor.fetchall()
        for row in user_ratings:
            userId = row["userId"]
            movieId = row["movieId"]
            rating = row["rating"]
            if userId not in user_ratings_dict:
                user_ratings_dict[userId] = {}
            user_ratings_dict[userId][movieId] = rating # {userId: {movieId: rating, ...}, ...}

    # 2. Compute Pearson correlation between the input ratings and other users
    user_similarities = {}  # dict {userId: similarity} (ground truth is the input ratings)
    
