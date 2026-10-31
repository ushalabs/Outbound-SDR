from contextlib import nullcontext
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
from bs4 import BeautifulSoup
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import inspect, text

from app.check_ai import AccessCheck
from app.db import engine, get_db
from app.main import app
from app.middleware import history
from app.models import Base, Prospect, Research
from app.services.ai import AIError, generate
from app.services.embeddings import embed
from app.services.fetching import FetchError, fetch_page, public_addresses, request, structured_companies
from app.services.prospects import csv_columns, preview_csv
from app.worker import recover_interrupted


def test_local_origin_host_and_body_guards():
    with TestClient(app, base_url="http://127.0.0.1") as client:
        assert (
            client.post(
                "/api/prospects", headers={"Origin": "https://untrusted.invalid"}, json={}
            ).status_code
            == 403
        )
        assert client.get("/api/health", headers={"Host": "untrusted.invalid"}).status_code == 400
        assert client.post("/api/prospects", content=b"x" * 3_000_001).status_code == 413
        assert client.get("/api/health").headers["x-content-type-options"] == "nosniff"


def test_rate_limit_is_shared_across_research_paths():
    history.clear()
    try:
        with TestClient(app, base_url="http://127.0.0.1") as client:
            for _ in range(10):
                assert client.post("/api/research", json={}).status_code == 422
            assert client.post("/api/semantic/search", json={"query": "test"}).status_code == 429
    finally:
        history.clear()


def test_mixed_public_private_dns_rejected(monkeypatch):
    monkeypatch.setattr(
        "socket.getaddrinfo",
        lambda *a, **k: [(2, 1, 6, "", ("8.8.8.8", 443)), (2, 1, 6, "", ("127.0.0.1", 443))],
    )
    with pytest.raises(FetchError, match="blocked"):
        public_addresses("rebind.invalid", 443)


def test_directory_only_extracts_explicit_companies_not_people():
    soup = BeautifulSoup(
        """<script type="application/ld+json">{"@type":"ItemList","itemListElement":[
      {"item":{"@type":"Organization","name":"Clearly synthetic company fixture","url":"https://fixture.invalid"}},
      {"item":{"@type":"Person","name":"Synthetic person","email":"never-extract@example.com"}},
      {"item":{"@type":"Organization","name":"Unknown website fixture"}}
    ]}</script>""",
        "html.parser",
    )
    records = structured_companies(soup, "https://directory.invalid")
    assert len(records) == 1 and records[0]["company_name"] == "Clearly synthetic company fixture"
    assert "email" not in records[0] and "full_name" not in records[0]


def test_redirect_policy_is_checked_before_target_page(monkeypatch):
    calls = []

    def respond(url):
        calls.append(url)
        if url == "https://public.invalid/robots.txt":
            return 404, "", "text/plain", url
        if url == "https://public.invalid/":
            return 302, "", "", "https://target.invalid/private"
        return 200, "User-agent: *\nDisallow: /private", "text/plain", url

    monkeypatch.setattr("app.services.fetching.request", respond)
    with pytest.raises(FetchError, match="robots"):
        fetch_page("https://public.invalid")
    assert "https://target.invalid/private" not in calls


def test_oversized_http_response_is_rejected(monkeypatch):
    response = SimpleNamespace(
        status=200,
        getheader=lambda key, default=None: {"Content-Length": "1000001", "Content-Type": "text/html"}.get(
            key, default
        ),
    )
    connection = SimpleNamespace(
        request=lambda *a, **k: None, getresponse=lambda: response, close=lambda: None
    )
    monkeypatch.setattr("app.services.fetching.PinnedHTTPS", lambda *a, **k: connection)
    with pytest.raises(FetchError, match="1 MB"):
        request("https://public.invalid")


def test_csv_mapping_and_limits():
    columns = csv_columns(
        '\ufeff"Company, legal name",website,"Full Name"\n"Fixture, Inc",fixture.invalid,Synthetic'
    )
    assert columns["headers"] == ["Company, legal name", "website", "Full Name"]
    assert columns["mapping"]["website"] == "website_url"
    with pytest.raises(HTTPException, match="Map each target"):
        preview_csv(None, "company,company_name,website\na,b,c", {})
    with pytest.raises(HTTPException) as error:
        preview_csv(None, "x" * 2_000_001, {})
    assert error.value.status_code == 413


def test_generation_network_error_is_useful(monkeypatch):
    def timeout(**kwargs):
        raise httpx.ReadTimeout("Isolated test timeout")

    fake = SimpleNamespace(models=SimpleNamespace(generate_content=timeout))
    monkeypatch.setattr("app.services.ai.client", lambda: nullcontext(fake))
    with pytest.raises(AIError, match="timed out"):
        generate(AccessCheck, "test", {})


def test_invalid_embedding_dimensions_rejected(monkeypatch):
    fake = SimpleNamespace(
        models=SimpleNamespace(
            get=lambda **kw: SimpleNamespace(supported_actions=["embedContent"]),
            embed_content=lambda **kw: SimpleNamespace(embeddings=[SimpleNamespace(values=[0.5, 0.2])]),
        )
    )
    monkeypatch.setattr("app.services.embeddings.client", lambda: nullcontext(fake))
    with pytest.raises(AIError, match="dimensions"):
        embed(["Isolated synthetic embedding test"])


@pytest.mark.integration
def test_interrupted_worker_run_is_failed_not_completed(live_client):
    client = live_client
    prospect = client.post(
        "/api/prospects",
        json={
            "company_name": "Isolated recovery fixture",
            "website_url": "https://recovery.invalid",
            "status": "qualified",
        },
    ).json()
    db = app.dependency_overrides[get_db]()
    row = db.get(Prospect, prospect["id"])
    row.status = "researching"
    job = Research(
        company_id=row.company_id,
        prospect_id=row.id,
        status="running",
        started_at=datetime.now(UTC) - timedelta(minutes=15),
        input_snapshot={"previous_prospect_status": "qualified"},
    )
    db.add(job)
    db.commit()
    assert recover_interrupted(db, datetime.now(UTC)) == 1
    assert job.status == "failed" and job.findings is None and row.status == "qualified"


@pytest.mark.integration
def test_frozen_migration_reproduces_schema():
    import uuid

    schema = "sdr_migration_test_" + uuid.uuid4().hex
    ddl = (Path(__file__).parents[1] / "migrations/versions/0001_core.sql").read_text(encoding="utf-8")
    with engine.connect() as db:
        transaction = db.begin()
        try:
            db.execute(text(f'CREATE SCHEMA "{schema}"'))
            for statement in ddl.replace("sdr.", f'"{schema}".').split(";\n"):
                if statement.strip():
                    db.execute(text(statement.strip()))
            assert set(inspect(db).get_table_names(schema=schema)) == {
                table.name for table in Base.metadata.sorted_tables
            }
            assert len(inspect(db).get_foreign_keys("outreach_drafts", schema=schema)) == 2
            assert (
                db.scalar(
                    text(
                        f"SELECT format_type(atttypid,atttypmod) FROM pg_attribute WHERE "
                        f"attrelid='\"{schema}\".research_chunks'::regclass AND attname='embedding'"
                    )
                )
                == "vector(768)"
            )
        finally:
            transaction.rollback()
    with engine.connect() as db:
        assert not inspect(db).has_schema(schema)
