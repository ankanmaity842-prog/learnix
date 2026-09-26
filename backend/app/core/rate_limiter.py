import time
from collections import defaultdict

from fastapi import HTTPException, Request, status


class RateLimiter:

    def __init__(
        self,
        max_requests: int = 60,
        window_seconds: int = 60,
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)

    def check(self, request: Request) -> None:
        client = request.client

        if client:
            key = client.host
        else:
            key = "unknown"

        now = time.time()

        self.requests[key] = [
            timestamp
            for timestamp in self.requests[key]
            if now - timestamp < self.window_seconds
        ]

        if len(self.requests[key]) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
            )

        self.requests[key].append(now)


default_rate_limiter = RateLimiter(
    max_requests=60,
    window_seconds=60,
)