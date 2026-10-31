import os
import uuid

import pytest
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import engine
from app.models import Base, Company, Prospect

pytestmark = [pytest.mark.integration, pytest.mark.skipif(os.getenv("RUN_LIVE_TESTS") != "1",
                                                          reason="Explicit RUN_LIVE_TESTS=1 required")]


def test_live_schema_and_vector():
    with engine.connect() as db:
        assert db.scalar(text("SELECT extversion FROM pg_extension WHERE extname='vector'"))
        assert db.scalar(text("SELECT version_num FROM sdr.alembic_version")) == "0001_core"
        actual = set(inspect(db).get_table_names(schema="sdr"))
        assert set(Base.metadata.tables.keys()) == {f"sdr.{name}" for name in actual - {"alembic_version"}}
        assert db.scalar(text("SELECT format_type(atttypid, atttypmod) FROM pg_attribute "
                              "WHERE attrelid='sdr.research_chunks'::regclass AND attname='embedding'")) == "vector(768)"


def test_isolated_roundtrip_and_constraints():
    schema = "sdr_test_" + uuid.uuid4().hex
    with engine.connect() as raw:
        transaction = raw.begin()
        try:
            raw.execute(text(f'CREATE SCHEMA "{schema}"'))
            connection = raw.execution_options(schema_translate_map={"sdr": schema})
            Base.metadata.create_all(connection)
            with Session(connection, join_transaction_mode="create_savepoint") as db:
                company = Company(name="Isolated fixture company", domain="fixture.invalid",
                                  website_url="https://fixture.invalid")
                db.add(company)
                db.flush()
                prospect = Prospect(company_id=company.id, full_name="Synthetic test contact",
                                    identity_key="a" * 64)
                db.add(prospect)
                db.flush()
                assert db.scalar(select(Prospect).where(Prospect.id == prospect.id)).company.name == company.name
                with pytest.raises(IntegrityError), db.begin_nested():
                    db.add(Company(name="Duplicate fixture", domain="fixture.invalid", website_url="https://fixture.invalid"))
                    db.flush()
                with pytest.raises(IntegrityError), db.begin_nested():
                    db.add(Prospect(company_id=uuid.uuid4(), identity_key="b" * 64))
                    db.flush()
                with pytest.raises(IntegrityError), db.begin_nested():
                    db.add(Prospect(company_id=company.id, identity_key="c" * 64, status="invalid"))
                    db.flush()
        finally:
            transaction.rollback()
    with engine.connect() as db:
        assert not inspect(db).has_schema(schema)
