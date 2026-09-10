"""FastAPI application: startup, CORS, URL routing, and the port-3000 server."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from db import init_database
from routes import movies, recommendations
# ---------- June 2026 extension starts ----------
from routes import tags
# ---------- June 2026 extension finishes ----------

API_PREFIX = "/movielens/api"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This async generator becomes an async context manager. Before yield:
    # startup; after yield: shutdown. Initialization completes before serving.
    init_database()
    yield


app = FastAPI(title="MovieLens Backend", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def invalid_request(request, exc):
    # Return useful field errors without echoing arbitrary input (e.g. NaN,
    # which Python's JSON decoder accepts but a JSON response cannot encode).
    detail = [{key: error[key] for key in ("loc", "msg", "type")} for error in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": detail})


# localhost:8080 and localhost:3000 differ by port: different origins. CORS
# permits reading the response and handles OPTIONS preflight for JSON POSTs.
# It is not authentication or protection from curl. This classroom API has no
# cookies or credentialed requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Routing uses both HTTP method and path, followed by input validation.
# Synchronous def handlers run in FastAPI's thread pool because sqlite3 blocks.
app.include_router(movies.router, prefix=API_PREFIX)
app.include_router(recommendations.router, prefix=API_PREFIX)
# ---------- June 2026 extension starts ----------
app.include_router(tags.router, prefix=API_PREFIX)
# ---------- June 2026 extension finishes ----------


if __name__ == "__main__":
    import uvicorn

    # Uvicorn accepts HTTP and calls the ASGI app. 0.0.0.0 listens on all
    # interfaces; use localhost in the local browser.
    uvicorn.run(app, host="0.0.0.0", port=3000)
