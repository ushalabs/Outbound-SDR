import os

import pytest
from sqlalchemy import select

from app.db import get_db
from app.main import app
from app.models import Research, ResearchSource
from app.research_schemas import ResearchFindings
from app.services.ai import AIError
from app.services.research import run_research, validate_grounding


def findings(source_id, quote):
    statement = {"text": "Fixture description", "references": [{"source_id": str(source_id), "quote": quote}]}
    return ResearchFindings.model_validate({"overview": statement, "products_services": [],
        "supported_facts": [statement], "potential_challenges_hypotheses": [],
        "qualification": "insufficient_information", "qualification_reasoning": "Isolated test fixture",
        "personalization_opportunities": [], "suggested_outreach_angle_hypothesis": "Ask a question",
        "confidence": "low", "missing_information": ["Actual business context"]})


def test_unverifiable_quotes_rejected():
    source = ResearchSource(id="source-1", evidence="This is the only stored evidence")
    with pytest.raises(AIError, match="citation"):
        validate_grounding(findings("source-1", "A completely invented quotation"), [source])
    validate_grounding(findings("source-1", "the only stored evidence"), [source])


@pytest.mark.integration
def test_research_failure_is_durable(live_client, monkeypatch):
    client = live_client
    prospect = client.post("/api/prospects", json={"company_name": "Isolated research fixture",
                           "website_url": "https://fixture.invalid"}).json()
    response = client.post("/api/research", json={"prospect_id": prospect["id"],
        "manual_notes": "This is an explicitly synthetic user-provided research fixture for an isolated test."})
    assert response.status_code == 202, response.text
    job_id = response.json()["id"]
    assert client.post("/api/research", json={"prospect_id": prospect["id"]}).status_code == 409
    db = app.dependency_overrides[get_db]()
    job = db.scalar(select(Research).where(Research.id == job_id))
    def fail(*args, **kwargs):
        raise AIError("Simulated provider outage in isolated test")
    monkeypatch.setattr("app.services.research.generate", fail)
    run_research(db, job)
    stored = client.get(f"/api/research/{job_id}").json()
    assert stored["status"] == "failed" and stored["findings"] is None
    assert stored["sources"][0]["kind"] == "user_provided"
    assert client.post(f"/api/research/{job_id}/rerun").status_code == 202


@pytest.mark.integration
def test_citation_correction_is_bounded_and_revalidated(live_client, monkeypatch):
    client = live_client
    prospect = client.post("/api/prospects", json={"company_name": "Isolated correction fixture",
                           "website_url": "https://correction.invalid"}).json()
    notes = "This is explicitly synthetic fixture evidence about community workshops and education programs."
    db = app.dependency_overrides[get_db]()
    for correction_succeeds in (True, False):
        calls = []
        def respond(schema, instruction, data, calls=calls, correction_succeeds=correction_succeeds):
            calls.append(instruction)
            quote = notes if correction_succeeds and len(calls) == 2 else "An invented quote unsupported by any evidence"
            return findings(data["sources"][0]["source_id"], quote)
        monkeypatch.setattr("app.services.research.generate", respond)
        queued = client.post("/api/research", json={"prospect_id": prospect["id"], "manual_notes": notes}).json()
        job = db.scalar(select(Research).where(Research.id == queued["id"]))
        run_research(db, job)
        assert len(calls) == 2
        assert job.status == ("completed" if correction_succeeds else "failed")
        if not correction_succeeds:
            assert job.findings is None and "citation validation" in job.error


@pytest.mark.integration
def test_live_public_research_and_gemini(live_client):
    if os.getenv("RUN_LIVE_TESTS") != "1":
        pytest.skip("Live provider access explicitly required")
    client = live_client
    prospect = client.post("/api/prospects", json={"company_name": "Python Software Foundation",
                           "website_url": "https://www.python.org/psf/",
                           "notes": "Controlled record in isolated integration-test schema"}).json()
    response = client.post("/api/research", json={"prospect_id": prospect["id"]})
    assert response.status_code == 202, response.text
    job_id = response.json()["id"]
    db = app.dependency_overrides[get_db]()
    job = db.scalar(select(Research).where(Research.id == job_id))
    run_research(db, job)
    stored = client.get(f"/api/research/{job_id}").json()
    assert stored["status"] == "completed", stored.get("error")
    assert stored["model"]
    assert stored["sources"][0]["url"].startswith("https://www.python.org")
    result = ResearchFindings.model_validate(stored["findings"])
    sources = db.scalars(select(ResearchSource).where(ResearchSource.research_id == job.id)).all()
    validate_grounding(result, sources)
    assert client.get(f"/api/research/{job_id}").json()["findings"] == stored["findings"]
