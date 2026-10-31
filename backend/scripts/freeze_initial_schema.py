"""Development-only generator for the initial frozen migration (not used at runtime)."""
from pathlib import Path

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex, CreateTable

from app.models import Base

target = Path(__file__).resolve().parents[1] / "migrations" / "versions" / "0001_core.sql"
if target.exists():
    raise RuntimeError("Initial migration is already frozen; create a new migration for schema changes")
parts = ["CREATE EXTENSION IF NOT EXISTS vector"]
for table in Base.metadata.sorted_tables:
    parts.append(str(CreateTable(table).compile(dialect=postgresql.dialect())).strip())
    for index in sorted(table.indexes, key=lambda item: item.name):
        parts.append(str(CreateIndex(index).compile(dialect=postgresql.dialect())).strip())
target.write_text(";\n".join(parts) + ";\n", encoding="utf-8")
print("Frozen initial schema DDL generated.")
