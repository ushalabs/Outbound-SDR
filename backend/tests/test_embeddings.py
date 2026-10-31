import pytest
from sqlalchemy import select

from app.db import get_db
from app.main import app
from app.models import Research, ResearchChunk, ResearchSource
from app.services.ai import AIError
from app.services.embeddings import embed_research


@pytest.mark.integration
def test_live_embedding_and_scoped_retrieval(live_client, monkeypatch):
    client = live_client
    prospect = client.post("/api/prospects", json={"company_name": "Isolated embedding fixture",
                           "website_url": "https://fixture.invalid"}).json()
    db = app.dependency_overrides[get_db]()
    job = Research(company_id=prospect["company"]["id"], prospect_id=prospect["id"], status="completed",
                   input_snapshot={"fixture": "isolated embedding integration"})
    db.add(job)
    db.flush()
    source = ResearchSource(research_id=job.id, title="Explicitly synthetic embedding test fixture",
        kind="user_provided", evidence="The isolated fixture supports open source education and community grant programs.")
    db.add(source)
    db.flush()
    db.add(ResearchChunk(source_id=source.id, text=source.evidence))
    db.commit()
    empty = client.post("/api/semantic/search", json={"query": "community education", "prospect_id": prospect["id"]})
    assert empty.json()["items"] == []
    response = client.post(f"/api/research/{job.id}/embeddings")
    assert response.status_code == 200, response.text
    assert response.json()["dimensions"] == 768
    chunk = db.scalar(select(ResearchChunk).where(ResearchChunk.source_id == source.id))
    assert len(chunk.embedding) == 768 and any(float(v) != 0 for v in chunk.embedding)
    result = client.post("/api/semantic/search", json={"query": "education and grant support", "prospect_id": prospect["id"]})
    assert result.status_code == 200, result.text
    match = result.json()["items"][0]
    assert match["company_id"] == prospect["company"]["id"] and match["source_kind"] == "user_provided"
    assert 0 < match["similarity"] <= 1
    other = client.post("/api/prospects", json={"company_name": "Unrelated isolated fixture", "website_url": "https://other.invalid"}).json()
    assert client.post("/api/semantic/search", json={"query": "education", "prospect_id": other["id"]}).json()["items"] == []
    def fail(*args, **kwargs):
        raise AIError("Simulated embedding failure in isolated test")
    monkeypatch.setattr("app.services.embeddings.embed", fail)
    with pytest.raises(AIError):
        embed_research(db, job)
    db.refresh(chunk)
    assert chunk.embedding is None and chunk.embedding_status == "failed"
