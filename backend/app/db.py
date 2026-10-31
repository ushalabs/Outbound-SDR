from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings


def database_url(direct: bool = False):
    settings = get_settings()
    secret = settings.direct_database_url if direct else settings.database_url
    raw = secret.get_secret_value()
    if raw.startswith("postgres://"):
        raw = "postgresql://" + raw[len("postgres://") :]
    return make_url(raw).set(drivername="postgresql+psycopg")


engine = create_engine(
    database_url(),
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
    connect_args={"connect_timeout": 10},
    hide_parameters=True,
)
if get_settings().test_schema:
    engine = engine.execution_options(schema_translate_map={"sdr": get_settings().test_schema})
SessionLocal = sessionmaker(engine, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise


Db = Annotated[Session, Depends(get_db)]
