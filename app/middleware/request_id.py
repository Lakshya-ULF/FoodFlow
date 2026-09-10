import uuid
import time
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


logger = logging.getLogger("foodflow.api")


class RequestIDMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        request_id = request.headers.get(
            "X-Request-ID",
            str(uuid.uuid4()),
        )

        request.state.request_id = request_id

        start_time = time.perf_counter()

        logger.info(
            "[%s] %s %s",
            request_id,
            request.method,
            request.url.path,
        )

        try:
            response = await call_next(request)

            duration_ms = (
                time.perf_counter() - start_time
            ) * 1000

            logger.info(
                "[%s] %s %s status=%s latency=%.2fms",
                request_id,
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
            )

            response.headers["X-Request-ID"] = request_id

            return response

        except Exception:
            duration_ms = (
                time.perf_counter() - start_time
            ) * 1000

            logger.exception(
                "[%s] %s %s failed latency=%.2fms",
                request_id,
                request.method,
                request.url.path,
                duration_ms,
            )

            raise