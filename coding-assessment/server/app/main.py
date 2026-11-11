import asyncio
import math
import time
import traceback
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import env
from app.db.mongo import connect_mongo_safe
from app.db.mongo_socket import start_mongo_socket, stop_mongo_socket
from app.db.seed import seed
from app.errors import AppError
from app.logger import logger
from app.modules.auth.routes import router as auth_router
from app.modules.events.routes import router as events_router
from app.modules.health.routes import router as health_router

_hits: dict[str, dict[str, float]] = {}


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response


class LoginRateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path.rstrip("/") or "/"
        if path != "/api/auth/login":
            return await call_next(request)
        key = request.client.host if request.client else "unknown"
        now = time.time() * 1000
        current = _hits.get(key)
        if current is None or now > current["reset_at"]:
            _hits[key] = {"count": 1, "reset_at": now + env.rate_limit_window_ms}
            return await call_next(request)
        current["count"] += 1
        if current["count"] > env.rate_limit_max:
            retry_after = str(max(0, math.ceil((current["reset_at"] - now) / 1000)))
            return JSONResponse(
                status_code=429,
                content={"message": "Too many requests"},
                headers={"Retry-After": retry_after},
            )
        return await call_next(request)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    seed()
    start_mongo_socket()
    asyncio.create_task(asyncio.to_thread(connect_mongo_safe))
    logger.info(f"Meridian API listening on :{env.port}")
    yield
    stop_mongo_socket()


app = FastAPI(lifespan=lifespan, redirect_slashes=False, docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(LoginRateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[env.cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIdMiddleware)

app.include_router(health_router, prefix="/api/health")
app.include_router(auth_router, prefix="/api/auth")
app.include_router(events_router, prefix="/api/events")


@app.exception_handler(AppError)
async def app_error(_request: Request, exc: AppError):
    error = {"code": exc.code, "message": exc.message}
    if exc.details is not None:
        error["details"] = exc.details
    return JSONResponse(status_code=exc.status, content={"error": error})


@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "ROUTE_NOT_FOUND",
                    "message": f"No route {request.method} {request.url.path}",
                }
            },
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "HTTP_ERROR", "message": str(exc.detail)}},
    )


@app.exception_handler(Exception)
async def unhandled(_request: Request, exc: Exception):
    logger.error("unhandled_error", {"message": str(exc), "stack": traceback.format_exc()})
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL", "message": "Unexpected server error"}},
    )
