from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging
from pathlib import Path
import re
import sys
from time import perf_counter
from traceback import format_tb
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import Config as cfg
from app.core.database import create_db_and_tables
from app.core.logging_setup import configure_logging
from app.api.router import router

IS_PRODUCTION = cfg.PRODUCT_MODE.value == "PROD"
LOGGING_CONFIG = configure_logging(production=IS_PRODUCTION)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info(
        "Application startup",
        extra={"event": "application.starting", "mode": cfg.PRODUCT_MODE.value},
    )
    try:
        await create_db_and_tables()
    except Exception as error:
        logger.error(
            "Application startup failed",
            extra={
                "event": "application.startup_failed",
                "mode": cfg.PRODUCT_MODE.value,
                "error_type": type(error).__name__,
                "stack_trace": "".join(format_tb(error.__traceback__)),
            },
        )
        raise
    logger.info(
        "Application started",
        extra={"event": "application.started", "mode": cfg.PRODUCT_MODE.value},
    )
    try:
        yield
    finally:
        logger.info(
            "Application shutdown",
            extra={"event": "application.stopping", "mode": cfg.PRODUCT_MODE.value},
        )


app = FastAPI(title=cfg.PROJECT_NAME, lifespan=lifespan)
app.include_router(router)


@app.middleware("http")
async def log_http_requests(request, call_next):
    incoming_request_id = request.headers.get("X-Request-ID", "")
    request_id = (
        incoming_request_id
        if re.fullmatch(r"[A-Za-z0-9._-]{1,64}", incoming_request_id)
        else uuid4().hex
    )
    request.state.request_id = request_id
    started_at = perf_counter()
    log_fields = {
        "event": "http.request",
        "request_id": request_id,
        "method": request.method,
        # Do not log query strings, which may contain user supplied secrets.
        "path": request.url.path,
    }

    try:
        response = await call_next(request)
    except Exception as error:
        duration_ms = round((perf_counter() - started_at) * 1000, 2)
        logger.error(
            "Unhandled request error",
            extra={
                **log_fields,
                "status_code": 500,
                "duration_ms": duration_ms,
                "error_type": type(error).__name__,
                "stack_trace": "".join(format_tb(error.__traceback__)),
            },
        )
        response = JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "request_id": request_id},
            headers={"Cache-Control": "no-store"},
        )
    else:
        duration_ms = round((perf_counter() - started_at) * 1000, 2)
        log_fields.update(
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        if response.status_code >= 500:
            logger.error("Request completed with server error", extra=log_fields)
        elif response.status_code >= 400:
            logger.warning("Request completed with client error", extra=log_fields)
        else:
            logger.info("Request completed", extra=log_fields)

    response.headers["X-Request-ID"] = request_id
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.CORS_ORIGINS,
    allow_origin_regex=cfg.CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)


# TODO: mb move redirects to frontend-side.
@app.get("/registration", include_in_schema=False)
async def registration_page() -> FileResponse:
    page_path = Path(__file__).resolve().parents[2] / "frontend" / "register.html"
    return FileResponse(page_path, media_type="text/html")


@app.get("/login", include_in_schema=False)
async def login_page() -> FileResponse:
    page_path = Path(__file__).resolve().parents[2] / "frontend" / "login.html"
    return FileResponse(page_path, media_type="text/html")


@app.get("/teacher-registration", include_in_schema=False)
async def teacher_registration_page() -> FileResponse:
    page_path = (
        Path(__file__).resolve().parents[2]
        / "frontend"
        / "teacher-register.html"
    )
    return FileResponse(page_path, media_type="text/html")


@app.get("/teacher-test", include_in_schema=False)
async def teacher_test_page() -> FileResponse:
    page_path = Path(__file__).resolve().parents[2] / "frontend" / "teacher-test.html"
    return FileResponse(page_path, media_type="text/html")


@app.get("/teacher-groups-test", include_in_schema=False)
async def teacher_groups_test_page() -> FileResponse:
    page_path = (
        Path(__file__).resolve().parents[2]
        / "frontend"
        / "teacher-groups-test.html"
    )
    return FileResponse(page_path, media_type="text/html")


@app.get("/balance-test", include_in_schema=False)
async def balance_test_page() -> FileResponse:
    page_path = Path(__file__).resolve().parents[2] / "frontend" / "balance-test.html"
    return FileResponse(page_path, media_type="text/html")


@app.get("/reward-test", include_in_schema=False)
async def reward_test_page() -> FileResponse:
    page_path = Path(__file__).resolve().parents[2] / "frontend" / "reward-test.html"
    return FileResponse(page_path, media_type="text/html")


if __name__ == "__main__":
    uvicorn.run(app, port=8000, log_config=LOGGING_CONFIG)
