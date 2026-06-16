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
  POST /movielens/api/tags/movies

────────────────────────────────────────────────────────────────────────────
THEORY · L4 Server-side/REST · FastAPI
  FastAPI is the "modern, fast (high-performance) web framework for building
  APIs with Python" from the lecture. It is built on two pieces the slides
  name explicitly: Pydantic (data validation, see models.py) and Starlette
  (the ASGI toolkit). It is built around async/await for high concurrency and
  auto-generates interactive docs (Swagger UI at /docs, ReDoc at /redoc).
  This file is the "Create a FastAPI App" step; the routers are the endpoints.
────────────────────────────────────────────────────────────────────────────
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import init_database
from routes import movies, recommendations
# ---------- tag search route import starts ----------
from routes import tags
# ---------- tag search route import finishes ----------

# The assignment's base URL is http://{domain}:3000/movielens/api, so every
# route is mounted under this prefix.
# THEORY · L2 HTTP · URL path: a URL is <scheme>://<host>:<port>/<path>?<query>.
# This constant is the <path> prefix shared by every resource the API exposes.
API_PREFIX = "/movielens/api"


# THEORY · L3 JavaScript / L4 REST · async + lifecycle:
#   `async def` defines a coroutine. The @asynccontextmanager decorator turns
#   this coroutine into a startup/shutdown hook: everything before `yield` runs
#   once when the server boots, everything after runs at shutdown. It mirrors
#   the Servlet life cycle from the lecture (init() on load, destroy() on
#   unload) — only here it is expressed with Python's async context-manager.
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
# THEORY · L2 HTTP · Same-Origin Policy & CORS:
#   An "origin" is the (scheme, host, port) tuple. Browsers block a script
#   loaded from one origin from reading responses from another origin (the
#   Same-Origin Policy) — a critical security mechanism. Our frontend
#   (localhost / file://) and backend (localhost:3000) are DIFFERENT origins,
#   so without cooperation the browser would refuse the fetch() calls.
#   Cross-Origin Resource Sharing (CORS) is the opt-in protocol that relaxes
#   this using response headers. This middleware makes the server answer with
#   `Access-Control-Allow-Origin: *` (and the matching Allow-Methods /
#   Allow-Headers), and it also handles the preflight OPTIONS request that the
#   browser sends before non-simple cross-origin requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the routers under the API base path.
# THEORY · L4 REST · Uniform Interface / URL mapping: each router groups the
#   endpoints for one resource; `prefix=API_PREFIX` performs the server-side
#   "URL mapping" the HTTP lecture lists as a core web-server function.
app.include_router(movies.router, prefix=API_PREFIX)
app.include_router(recommendations.router, prefix=API_PREFIX)
# --- EXAM Q ---
# ---------- tag search route registration starts ----------
app.include_router(tags.router, prefix=API_PREFIX)
# ---------- tag search route registration finishes ----------


if __name__ == "__main__":
    # Allows `python main.py` to launch the server on the required port 3000.
    # THEORY · L4 Server-side/REST · Uvicorn (ASGI):
    #   ASGI = Asynchronous Server Gateway Interface, the standard contract
    #   between an async Python app and the network. Uvicorn is the ASGI server
    #   (built on uvloop + httptools) that actually accepts TCP connections,
    #   parses HTTP, and calls our FastAPI `app`. host="0.0.0.0" binds every
    #   network interface so the app is reachable on the local network, not
    #   only on 127.0.0.1.
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3000)
