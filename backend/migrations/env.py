from alembic import context
from sqlalchemy import create_engine, pool, text

from app.db import database_url
from app.models import Base


def run_migrations_online():
    url = database_url(direct=True)
    if "-pooler" in (url.host or ""):
        raise RuntimeError("DIRECT_DATABASE_URL must use a direct, non-pooler connection")
    connectable = create_engine(
        url, poolclass=pool.NullPool, hide_parameters=True, connect_args={"connect_timeout": 10}
    )
    with connectable.connect() as connection:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS sdr"))
        connection.commit()
        context.configure(
            connection=connection,
            target_metadata=Base.metadata,
            include_schemas=True,
            version_table_schema="sdr",
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    raise RuntimeError("Use online migrations with the direct database connection")
else:
    run_migrations_online()
