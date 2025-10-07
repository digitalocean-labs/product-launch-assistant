import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from typing import Dict
from starlette.middleware.base import BaseHTTPMiddleware

from .config import DIGITALOCEAN_INFERENCE_KEY, SERPER_API_KEY


class RedactSecretsFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        redactions = {
            DIGITALOCEAN_INFERENCE_KEY or "": "[REDACTED]",
            SERPER_API_KEY or "": "[REDACTED]"
        }
        msg = str(record.getMessage())
        for secret, replacement in redactions.items():
            if secret:
                msg = msg.replace(secret, replacement)
        record.msg = msg
        return True


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        response.headers.setdefault("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
        return response


class RateLimiterMiddleware(BaseHTTPMiddleware):
    requests_per_minute: int = 60
    _ip_to_hits: Dict[str, list] = {}

    async def dispatch(self, request: Request, call_next):
        from time import time
        now = time()
        window = 60.0
        client_ip = request.client.host if request.client else "unknown"
        hits = self._ip_to_hits.get(client_ip, [])
        hits = [t for t in hits if now - t < window]
        if len(hits) >= self.requests_per_minute:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Try again later."})
        hits.append(now)
        self._ip_to_hits[client_ip] = hits
        return await call_next(request)


