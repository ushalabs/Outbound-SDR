import pytest

from app.db import get_db
from app.main import app
from app.models import OutreachDraft, Research
from app.services.outreach import append_version


@pytest.mark.integration
def test_approval_state_machine_audit_and_export(live_client):
    client = live_client
    prospect = client.post(
        "/api/prospects",
        json={"company_name": "Isolated approval fixture", "website_url": "https://approval.invalid"},
    ).json()
    db = app.dependency_overrides[get_db]()
    research = Research(
        company_id=prospect["company"]["id"],
        prospect_id=prospect["id"],
        status="completed",
        input_snapshot={"fixture": "isolated state machine verification"},
    )
    db.add(research)
    db.flush()
    draft = OutreachDraft(prospect_id=prospect["id"], research_id=research.id)
    db.add(draft)
    db.flush()
    append_version(
        db,
        draft,
        "Clearly synthetic review fixture",
        "Synthetic isolated draft body",
        "Optional conversation",
        {},
        {},
        "created",
    )
    db.commit()
    path = f"/api/approvals/{draft.id}"

    def action(name, version, note=None):
        return client.post(path + "/action", json={"action": name, "expected_version": version, "note": note})

    assert client.get("/api/approvals/counts").json()["pending"] == 1
    assert client.get(path + "/export").status_code == 409
    assert action("approve", 1).json()["status"] == "approved"
    export = client.get(path + "/export").json()
    assert export["version"] == 1 and export["delivery_status"] == "not_sent"
    assert action("approve", 1).status_code == 409
    edited = client.patch(
        f"/api/outreach/{draft.id}",
        json={"subject": "Changed fixture", "body": "Changed content", "expected_version": 1},
    ).json()
    assert edited["status"] == "pending" and edited["current_version"] == 2
    assert client.get(path + "/export").status_code == 409
    assert action("reject", 2, "Needs a better opener").json()["status"] == "rejected"
    assert action("approve", 2).status_code == 409
    reopened = action("reopen", 2, "Explicit new review").json()
    assert reopened["status"] == "pending" and reopened["current_version"] == 3
    assert action("approve", 2).status_code == 409
    assert action("approve", 3).json()["status"] == "approved"
    archived = action("archive", 3).json()
    assert archived["status"] == "archived"
    assert action("reopen", 3).status_code == 409
    assert (
        client.patch(
            f"/api/outreach/{draft.id}", json={"subject": "Invalid", "body": "Invalid", "expected_version": 3}
        ).status_code
        == 409
    )
    history = client.get(f"/api/outreach/{draft.id}").json()
    rejected = next(e for e in history["events"] if e["action"] == "rejected")
    assert rejected["note"] == "Needs a better opener"
    assert len([e for e in history["events"] if e["action"] == "approved"]) == 2
    events = client.get("/api/activity").json()["items"]
    assert any(e["event_type"] == "draft.exported" for e in events)
    assert client.get("/api/approvals?status=archived&search=fixture").json()["total"] == 1
    guarded = OutreachDraft(prospect_id=prospect["id"], research_id=research.id)
    db.add(guarded)
    db.flush()
    append_version(db, guarded, "Opt-out fixture", "Isolated opt-out draft", "Question", {}, {}, "created")
    db.commit()
    guard_path = f"/api/approvals/{guarded.id}"
    assert (
        client.post(guard_path + "/action", json={"action": "approve", "expected_version": 1}).status_code
        == 200
    )
    client.post("/api/prospects/bulk", json={"ids": [prospect["id"]], "action": "do_not_contact"})
    assert client.get(guard_path + "/export").status_code == 409
    client.patch(
        f"/api/outreach/{guarded.id}",
        json={"subject": "Needs review", "body": "Changed", "expected_version": 1},
    )
    assert (
        client.post(guard_path + "/action", json={"action": "approve", "expected_version": 2}).status_code
        == 409
    )
