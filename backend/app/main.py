from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.logging_config import configure_logging
from app.middleware import external_request_limits
from app.routes.prospects import router as prospect_router
from app.routes.research import router as research_router
from app.routes.semantic import router as semantic_router
from app.routes.system import router as system_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_settings()
    configure_logging()
    yield


app = FastAPI(title="Think AI Works · Outbound SDR", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
                   allow_methods=["GET", "POST", "PATCH", "DELETE"], allow_headers=["Content-Type"])
app.include_router(system_router)
app.include_router(prospect_router)
app.include_router(research_router)
app.include_router(semantic_router)
app.middleware("http")(external_request_limits)


@app.exception_handler(SQLAlchemyError)
async def database_error(request: Request, exc: SQLAlchemyError):
    # Never include connection strings, SQL parameters or personal records in API errors.
    return JSONResponse(status_code=503, content={"detail": "Database operation failed. Check connectivity and migrations."})


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    # Validation errors must not echo input values (which may contain credentials).
    return JSONResponse(status_code=422, content={"detail": [
        {"location": list(e["loc"]), "message": e["msg"], "type": e["type"]} for e in exc.errors()
    ]})


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "outbound-sdr", "email_sending_enabled": False}
