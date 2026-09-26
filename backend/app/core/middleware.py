import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.logging import get_logger


logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        request_id = str(uuid4())
        start_time = time.perf_counter()

        response = await call_next(request)

        duration = time.perf_counter() - start_time

        response.headers["X-Request-ID"] = request_id

        logger.info(
            "%s %s %s %.4fs",
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )

        return response