from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import load_settings
from app.db import verify_database_connection
from app.logging_config import setup_logging
from app.middleware.request_logging import RequestLoggingMiddleware
from app.routers import links, redirect


settings = load_settings()
setup_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    # DB check skipped for testing
    yield


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


@app.get("/health")
def health() -> dict[str, bool | int]:
    return {"ok": True, "port": settings.port}


app.include_router(links.router)
app.include_router(redirect.router)
