import time
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Stores IP mapping to (timestamp, count)
        self._clients: Dict[str, Tuple[float, int]] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()

        if client_ip in self._clients:
            window_start, count = self._clients[client_ip]
            if current_time - window_start > self.window_seconds:
                # Reset window
                self._clients[client_ip] = (current_time, 1)
            else:
                if count >= self.max_requests:
                    # Return 429 Too Many Requests using the standard ErrorResponse schema
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": {
                                "code": "TOO_MANY_REQUESTS",
                                "message": "Rate limit exceeded. Please try again later.",
                                "details": f"Limit: {self.max_requests} requests per {self.window_seconds}s."
                            }
                        }
                    )
                self._clients[client_ip] = (window_start, count + 1)
        else:
            self._clients[client_ip] = (current_time, 1)

        response = await call_next(request)
        return response
