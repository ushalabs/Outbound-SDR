import time
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse

history = defaultdict(deque)


async def external_request_limits(request: Request, call_next):
    path = request.url.path
    limit = 10 if path == "/api/discovery/preview" else None
    if request.method == "POST" and limit:
        key = (request.client.host if request.client else "local", path)
        queue = history[key]
        now = time.monotonic()
        while queue and queue[0] < now - 60:
            queue.popleft()
        if len(queue) >= limit:
            return JSONResponse(status_code=429, content={"detail": "Please wait a minute before fetching more sources."},
                                headers={"Retry-After": "60"})
        queue.append(now)
    return await call_next(request)
