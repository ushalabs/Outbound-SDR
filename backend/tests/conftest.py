import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import engine, get_db
from app.main import app
from app.middleware import history
from app.models import Base


@pytest.fixture
def live_client():
    if os.getenv("RUN_LIVE_TESTS") != "1":
        pytest.skip("Explicit RUN_LIVE_TESTS=1 required")
    history.clear()
    schema = "sdr_test_" + uuid.uuid4().hex
    with engine.connect() as raw:
        transaction = raw.begin()
        raw.execute(text(f'CREATE SCHEMA "{schema}"'))
        connection = raw.execution_options(schema_translate_map={"sdr": schema})
        Base.metadata.create_all(connection)
        with Session(connection, join_transaction_mode="create_savepoint", expire_on_commit=False) as db:
            app.dependency_overrides[get_db] = lambda: db
            try:
                with TestClient(app, base_url="http://127.0.0.1") as client:
                    yield client
            finally:
                app.dependency_overrides.clear()
        transaction.rollback()
