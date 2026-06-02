"""
MovieLens Backend — FastAPI application entry point.

Wires everything together:
  - initializes the SQLite DB on first startup,
  - enables CORS (required by the assignment),
  - mounts the route modules under the `/movielens/api` base path, and
  - runs uvicorn on port 3000 when executed directly.

Full endpoint paths (base URL http://{domain}:3000/movielens/api):
  GET  /movielens/api/movies?search={keyword}
  GET  /movielens/api/ratings/{movieId}
  POST /movielens/api/movies
  POST /movielens/api/recommendations
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import init_database
from routes import movies, recommendations

# The assignment's base URL is http://{domain}:3000/movielens/api, so every
# route is mounted under this prefix.
API_PREFIX = "/movielens/api"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs on startup: build + populate the DB if it doesn't exist yet.
    print("Starting up...")
    init_database()
    yield
    # Runs on shutdown.
    print("Shutting down...")


app = FastAPI(title="MovieLens Backend", lifespan=lifespan)

# CORS: allow the (file://-served or any-origin) frontend to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the routers under the API base path.
app.include_router(movies.router, prefix=API_PREFIX)
app.include_router(recommendations.router, prefix=API_PREFIX)


if __name__ == "__main__":
    # Allows `python main.py` to launch the server on the required port 3000.
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3000)
