"""Small structured access-log middleware."""

import json
import logging
import time
from collections.abc import Awaitable, Callable
from typing import override

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

LOGGER = logging.getLogger("app.access")


class StructuredAccessMiddleware(BaseHTTPMiddleware):
    """Log method, path, status, and latency without sensitive request data."""

    @override
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Record a sanitized structured event for one HTTP exchange."""
        started = time.perf_counter()
        response = await call_next(request)
        LOGGER.info(
            json.dumps(
                {
                    "event": "http_request",
                    "method": request.method,
                    "path": request.url.path,
                    "status": response.status_code,
                    "durationMs": round((time.perf_counter() - started) * 1000, 2),
                },
                ensure_ascii=False,
            )
        )
        return response
