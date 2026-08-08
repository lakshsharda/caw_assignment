import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.logging_config import log_event, new_request_id, request_id_ctx


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        req_id = new_request_id()
        token = request_id_ctx.set(req_id)
        started = time.perf_counter()
        try:
            log_event(
                logging.INFO,
                "request received",
                method=request.method,
                path=request.url.path,
            )
            response = await call_next(request)
            duration_ms = round((time.perf_counter() - started) * 1000)
            log_event(
                logging.INFO,
                "response sent",
                status=response.status_code,
                duration_ms=duration_ms,
            )
            return response
        finally:
            request_id_ctx.reset(token)
