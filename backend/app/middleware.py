import time
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse

from app.config import get_settings

history = defaultdict(deque)


async def external_request_limits(request: Request, call_next):
    path = request.url.path
    if request.method in ("POST", "PATCH", "DELETE"):
        origin = request.headers.get("origin")
        allowed = {
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        }
        if get_settings().app_env == "test":
            allowed.update({"http://127.0.0.1:5174", "http://127.0.0.1:8001"})
        if origin and origin not in allowed:
            return JSONResponse(
                status_code=403,
                content={"detail": "This local workspace rejects changes from other origins."},
            )
        length = request.headers.get("content-length", "0")
        if length.isdigit() and int(length) > 3_000_000:
            return JSONResponse(
                status_code=413, content={"detail": "Request exceeds the 3 MB transport limit."}
            )
    category = (
        "discovery"
        if path == "/api/discovery/preview"
        else "ai"
        if path.startswith(("/api/research", "/api/outreach", "/api/semantic"))
        else None
    )
    limit = 10 if category else None
    if request.method == "POST" and limit:
        key = (request.client.host if request.client else "local", category)
        queue = history[key]
        now = time.monotonic()
        while queue and queue[0] < now - 60:
            queue.popleft()
        if len(queue) >= limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Please wait a minute before fetching more sources."},
                headers={"Retry-After": "60"},
            )
        queue.append(now)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = "frame-ancestors 'none'"
    return response
