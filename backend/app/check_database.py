"""Read-only connection diagnostic; emits no credentials or application records."""
import json
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.db import database_url
from app.logging_config import redact


def main():
    for name, direct in (("runtime", False), ("migration", True)):
        try:
            engine = create_engine(database_url(direct), connect_args={"connect_timeout": 10},
                                   hide_parameters=True)
            with engine.connect() as db:
                tables = db.execute(text("SELECT table_schema, table_name FROM information_schema.tables "
                                         "WHERE table_schema NOT IN ('pg_catalog', 'information_schema') "
                                         "AND table_type='BASE TABLE' ORDER BY table_schema, table_name")).all()
                print(json.dumps({"connection": name, "status": "connected", "existing_tables":
                                  [f"{schema}.{table}" for schema, table in tables]}))
            engine.dispose()
        except (SQLAlchemyError, ValueError, OSError) as exc:
            print(json.dumps({"connection": name, "status": "failed", "error": redact(str(exc))}))
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
