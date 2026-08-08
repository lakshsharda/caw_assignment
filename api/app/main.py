from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import load_settings, Environment
from app.logging_config import setup_logging
from app.middleware.request_logging import RequestLoggingMiddleware
from app.routers import links, redirect


settings = load_settings()
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Log startup with environment info (without secrets)
    logger.info(
        "Service starting",
        extra={
            "environment": settings.app_env.value,
            "port": settings.port,
            "log_level": settings.log_level,
        },
    )
    yield
    logger.info("Service shutting down")


app = FastAPI(title="URL Shortener", lifespan=lifespan)
app.add_middleware(RequestLoggingMiddleware)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(_, exc: RequestValidationError) -> JSONResponse:
    detail = [
        {
            "loc": error.get("loc"),
            "msg": error.get("msg"),
            "type": error.get("type"),
        }
        for error in exc.errors()
    ]
    return JSONResponse(status_code=400, content={"detail": detail})


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc: Exception) -> JSONResponse:
    """Handle unhandled exceptions with environment-aware error detail level.

    In development/staging: include error details for debugging
    In production: generic message only (security best practice)
    """
    show_details = settings.app_env in (Environment.development, Environment.staging)

    body: dict = {"error": "Internal Server Error"}
    if show_details:
        body["details"] = str(exc)
        body["environment"] = settings.app_env.value

    logger.error(
        "Unhandled exception",
        extra={"exception": str(exc), "path": request.url.path},
        exc_info=True,
    )

    return JSONResponse(status_code=500, content=body)


@app.get("/health")
def health() -> dict[str, bool | int | str]:
    """Health check endpoint. Used by load balancers and orchestrators."""
    return {
        "ok": True,
        "port": settings.port,
        "environment": settings.app_env.value,
    }


app.include_router(links.router)
app.include_router(redirect.router)
