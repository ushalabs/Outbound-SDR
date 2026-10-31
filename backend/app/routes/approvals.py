import json
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select

from app.db import Db
from app.models import ActivityLog, ApprovalEvent, Company, OutreachDraft, Prospect
from app.routes.outreach import draft_json, locked_draft
from app.services.outreach import append_version, current_version
from app.services.prospects import activity

router = APIRouter(prefix="/api", tags=["Review and activity"])
TRANSITIONS = {"pending": {"approve": "approved", "reject": "rejected", "archive": "archived"},
               "approved": {"archive": "archived"}, "rejected": {"archive": "archived", "reopen": "pending"},
               "archived": {}}


class ReviewAction(BaseModel):
    action: Literal["approve", "reject", "archive", "reopen"]
    expected_version: int = Field(ge=1)
    note: str | None = Field(default=None, max_length=2000)


@router.get("/approvals/counts")
def approval_counts(db: Db):
    counts = dict(db.execute(select(OutreachDraft.status, func.count()).group_by(OutreachDraft.status)).all())
    return {status: counts.get(status, 0) for status in TRANSITIONS}


@router.get("/approvals")
def review_queue(db: Db, status: Literal["pending", "approved", "rejected", "archived"] | None = None,
                 search: str = Query("", max_length=200), page: int = Query(1, ge=1),
                 page_size: int = Query(20, ge=1, le=100)):
    statement = select(OutreachDraft).join(Prospect).join(Company)
    if status:
        statement = statement.where(OutreachDraft.status == status)
    if search:
        term = "%" + search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        statement = statement.where(or_(Prospect.full_name.ilike(term, escape="\\"),
                                        Company.name.ilike(term, escape="\\")))
    total = db.scalar(select(func.count()).select_from(statement.subquery()))
    rows = db.scalars(statement.order_by(OutreachDraft.updated_at.desc()).offset((page-1)*page_size)
                      .limit(page_size)).all()
    return {"items": [draft_json(db, d) for d in rows], "total": total, "page": page, "page_size": page_size}


@router.post("/approvals/{draft_id}/action")
def review_action(draft_id: UUID, data: ReviewAction, db: Db):
    draft = locked_draft(db, draft_id)
    if draft.current_version != data.expected_version:
        raise HTTPException(409, "The draft version changed. Reload before reviewing.")
    target = TRANSITIONS[draft.status].get(data.action)
    if not target:
        raise HTTPException(409, f"Cannot {data.action} a {draft.status} draft")
    prospect = db.get(Prospect, draft.prospect_id)
    if data.action == "approve" and prospect.do_not_contact:
        raise HTTPException(409, "Do-not-contact prospects cannot be approved")
    version = current_version(db, draft)
    if data.action == "reopen":
        version = append_version(db, draft, version.subject, version.body, version.cta,
                                 version.personalization, version.context, "reopened")
        if data.note:
            event = db.scalar(select(ApprovalEvent).where(ApprovalEvent.version_id == version.id))
            event.note = data.note
    else:
        draft.status = target
        action = {"approve": "approved", "reject": "rejected", "archive": "archived"}[data.action]
        db.add(ApprovalEvent(draft_id=draft.id, version_id=version.id, action=action, note=data.note))
        activity(db, f"draft.{action}", "draft", draft.id, version=draft.current_version)
    db.commit()
    return draft_json(db, draft)


@router.get("/approvals/{draft_id}/export")
def export_approved(draft_id: UUID, db: Db):
    draft = locked_draft(db, draft_id)
    if draft.status != "approved":
        raise HTTPException(409, "Only an approved current version can be exported")
    prospect, version = db.get(Prospect, draft.prospect_id), current_version(db, draft)
    if prospect.do_not_contact:
        raise HTTPException(409, "Do-not-contact prospects cannot be exported")
    payload = {"draft_id": str(draft.id), "version": version.version, "status": "approved_draft",
               "delivery_status": "not_sent", "recipient_email": prospect.email,
               "subject": version.subject, "body": version.body}
    activity(db, "draft.exported", "draft", draft.id, version=version.version)
    db.commit()
    return Response(json.dumps(payload, ensure_ascii=False, indent=2), media_type="application/json",
                    headers={"Content-Disposition": f'attachment; filename="approved-draft-{draft.id}-v{version.version}.json"'})


@router.get("/activity")
def activity_history(db: Db, page: int = Query(1, ge=1), page_size: int = Query(30, ge=1, le=100),
                     event_type: str = Query("", max_length=80)):
    statement = select(ActivityLog)
    if event_type:
        statement = statement.where(ActivityLog.event_type == event_type)
    total = db.scalar(select(func.count()).select_from(statement.subquery()))
    rows = db.scalars(statement.order_by(ActivityLog.created_at.desc(), ActivityLog.id)
                      .offset((page-1)*page_size).limit(page_size)).all()
    return {"items": [{name: getattr(row, name) for name in ("id", "event_type", "entity_type", "entity_id",
                      "details", "created_at")} for row in rows], "total": total, "page": page, "page_size": page_size}
