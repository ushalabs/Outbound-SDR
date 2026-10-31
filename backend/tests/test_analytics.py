from datetime import UTC, datetime, timedelta

import pytest

from app.db import get_db
from app.main import app
from app.models import OutreachDraft, Research
from app.services.outreach import append_version


@pytest.mark.integration
def test_real_aggregates_empty_ranges_and_decisions(live_client):
    client = live_client
    empty = client.get("/api/analytics").json()
    assert empty["totals"]["prospects"] == 0 and empty["prospect_growth_pct"] is None
    assert len(empty["daily"]) == 30 and sum(d["prospects"] for d in empty["daily"]) == 0
    assert empty["approval_turnaround_minutes"] is None and empty["statuses"] == []
    prospect = client.post(
        "/api/prospects",
        json={
            "company_name": "Isolated analytics fixture",
            "website_url": "https://analytics.invalid",
            "industry": "Education",
        },
    ).json()
    assert client.get("/api/analytics").json()["totals"]["prospects"] == 1
    client.post(
        "/api/prospects/bulk", json={"ids": [prospect["id"]], "action": "status", "status": "qualified"}
    )
    db = app.dependency_overrides[get_db]()
    research = Research(
        company_id=prospect["company"]["id"],
        prospect_id=prospect["id"],
        status="completed",
        input_snapshot={"fixture": "isolated analytics"},
        finished_at=datetime.now(UTC),
    )
    db.add(research)
    db.flush()
    draft = OutreachDraft(prospect_id=prospect["id"], research_id=research.id)
    db.add(draft)
    db.flush()
    append_version(
        db,
        draft,
        "Isolated dashboard fixture",
        "Clearly synthetic isolated draft",
        "Question",
        {},
        {},
        "created",
    )
    db.commit()
    pending = client.get("/api/analytics").json()
    assert pending["totals"]["researched"] == 1 and pending["totals"]["qualified"] == 1
    assert pending["totals"]["pending"] == 1 and pending["totals"]["generated"] == 1
    assert pending["research_coverage_pct"] == 100 and pending["industries"] == [
        {"name": "Education", "value": 1}
    ]
    assert sum(d["research"] for d in pending["daily"]) == 1
    assert (
        client.post(
            f"/api/approvals/{draft.id}/action", json={"action": "approve", "expected_version": 1}
        ).status_code
        == 200
    )
    approved = client.get("/api/analytics").json()
    assert approved["totals"]["pending"] == 0 and approved["totals"]["approved"] == 1
    assert sum(d["approved"] for d in approved["daily"]) == 1
    assert approved["approval_turnaround_minutes"] is not None
    assert any(e["event_type"] == "draft.approved" for e in approved["recent_activity"])
    future = (datetime.now(UTC) + timedelta(days=5)).date().isoformat()
    assert client.get(f"/api/analytics?start={future}&end={future}").json()["totals"]["prospects"] == 0
    assert client.get("/api/analytics?start=2026-11-02&end=2026-11-01").status_code == 422
