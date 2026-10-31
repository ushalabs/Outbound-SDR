import pytest

from app.db import get_db
from app.main import app
from app.models import Research, ResearchChunk, ResearchSource
from app.services.embeddings import embed_research

SENDER = {"name": "Isolated QA reviewer", "company": "Clearly synthetic QA sender",
          "value_proposition": "An optional conversation about better internal tools, without claiming any results."}


@pytest.mark.integration
def test_real_personalization_versions_and_optout(live_client):
    client = live_client
    db = app.dependency_overrides[get_db]()
    drafts, prospects = [], []
    examples = [("education", "The clearly synthetic education fixture organizes community coding workshops and teacher training."),
                ("robotics", "The clearly synthetic robotics fixture develops underwater inspection robots and marine navigation sensors.")]
    for label, evidence in examples:
        prospect = client.post("/api/prospects", json={"company_name": f"Isolated {label} fixture",
                               "website_url": f"https://{label}.invalid"}).json()
        prospects.append(prospect)
        job = Research(company_id=prospect["company"]["id"], prospect_id=prospect["id"], status="completed",
                       input_snapshot={"fixture": "explicit isolated AI generation test"})
        db.add(job)
        db.flush()
        source = ResearchSource(research_id=job.id, title="Clearly synthetic isolated source fixture",
                                kind="user_provided", evidence=evidence)
        db.add(source)
        db.flush()
        db.add(ResearchChunk(source_id=source.id, text=evidence))
        db.commit()
        embed_research(db, job)
        response = client.post("/api/outreach/generate", json={"prospect_id": prospect["id"], "sender": SENDER})
        assert response.status_code == 201, response.text
        draft = response.json()
        drafts.append(draft)
        assert draft["status"] == "pending" and draft["current_version"] == 1
        for ref in draft["versions"][0]["context"]["references"]:
            assert ref["quote"].casefold() in evidence.casefold()
    assert drafts[0]["versions"][0]["body"] != drafts[1]["versions"][0]["body"]
    original = drafts[0]["versions"][0]
    edited = client.patch(f"/api/outreach/{drafts[0]['id']}", json={"subject": original["subject"],
                          "body": original["body"] + "\nHuman-edited isolated test note.", "expected_version": 1})
    assert edited.status_code == 200, edited.text
    assert edited.json()["current_version"] == 2
    assert edited.json()["versions"][1]["body"] == original["body"]
    regenerated = client.post(f"/api/outreach/{drafts[0]['id']}/regenerate",
        json={"prospect_id": prospects[0]["id"], "tone": "concise", "sender": SENDER})
    assert regenerated.status_code == 200, regenerated.text
    assert regenerated.json()["current_version"] == 3 and len(regenerated.json()["versions"]) == 3
    assert client.get(f"/api/outreach/{drafts[0]['id']}").json()["current_version"] == 3
    client.post("/api/prospects/bulk", json={"ids": [prospects[0]["id"]], "action": "do_not_contact"})
    blocked = client.post("/api/outreach/generate", json={"prospect_id": prospects[0]["id"], "sender": SENDER})
    assert blocked.status_code == 422 and "opted out" in blocked.text
