from fastapi import APIRouter
from sqlalchemy import func, select, text

from app.db import Db
from app.models import Company, Prospect

router = APIRouter(prefix="/api")


@router.get("/system/database")
def database_status(db: Db):
    db.execute(text("SELECT 1"))
    vector_version = db.execute(text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")).scalar()
    revision = db.execute(text("SELECT version_num FROM sdr.alembic_version")).scalar()
    return {
        "status": "connected",
        "vector_version": vector_version,
        "schema_revision": revision,
        "companies": db.scalar(select(func.count()).select_from(Company)),
        "prospects": db.scalar(select(func.count()).select_from(Prospect)),
    }
