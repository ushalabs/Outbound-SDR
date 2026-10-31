from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select

from app.db import Db
from app.models import ApprovalEvent, DraftVersion, OutreachDraft, Prospect
from app.outreach_schemas import DraftEdit, OutreachGenerate
from app.services.ai import AIError
from app.services.outreach import append_version, create_draft, current_version, generate_content

router = APIRouter(prefix="/api/outreach", tags=["Outreach drafts"])


def draft_json(db, draft):
    prospect = db.get(Prospect, draft.prospect_id)
    return {
        "id": draft.id,
        "prospect_id": draft.prospect_id,
        "research_id": draft.research_id,
        "status": draft.status,
        "tone": draft.tone,
        "current_version": draft.current_version,
        "sender_context": draft.sender_context,
        "created_at": draft.created_at,
        "updated_at": draft.updated_at,
        "company_name": prospect.company.name if prospect else "Deleted prospect",
        "contact_name": prospect.full_name if prospect else None,
        "versions": [
            {
                name: getattr(v, name)
                for name in (
                    "id",
                    "version",
                    "subject",
                    "body",
                    "cta",
                    "personalization",
                    "context",
                    "created_at",
                )
            }
            for v in db.scalars(
                select(DraftVersion)
                .where(DraftVersion.draft_id == draft.id)
                .order_by(DraftVersion.version.desc())
            ).all()
        ],
        "events": [
            {name: getattr(e, name) for name in ("id", "action", "version_id", "note", "created_at")}
            for e in db.scalars(
                select(ApprovalEvent)
                .where(ApprovalEvent.draft_id == draft.id)
                .order_by(ApprovalEvent.created_at)
            ).all()
        ],
    }


def locked_draft(db, draft_id):
    draft = db.scalar(select(OutreachDraft).where(OutreachDraft.id == draft_id).with_for_update())
    if not draft:
        raise HTTPException(404, "Draft not found")
    return draft


@router.post("/generate", status_code=201)
def generate_outreach(data: OutreachGenerate, db: Db):
    try:
        draft = create_draft(db, data)
        return draft_json(db, draft)
    except AIError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("")
def list_drafts(
    db: Db,
    prospect_id: UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    statement = select(OutreachDraft)
    if prospect_id:
        statement = statement.where(OutreachDraft.prospect_id == prospect_id)
    total = db.scalar(select(func.count()).select_from(statement.subquery()))
    records = db.scalars(
        statement.order_by(OutreachDraft.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return {
        "items": [draft_json(db, d) for d in records],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{draft_id}")
def get_draft(draft_id: UUID, db: Db):
    draft = db.get(OutreachDraft, draft_id)
    if not draft:
        raise HTTPException(404, "Draft not found")
    return draft_json(db, draft)


@router.patch("/{draft_id}")
def edit_draft(draft_id: UUID, data: DraftEdit, db: Db):
    draft = locked_draft(db, draft_id)
    if draft.status == "archived":
        raise HTTPException(409, "Archived drafts cannot be edited")
    if data.expected_version != draft.current_version:
        raise HTTPException(409, "This draft changed since you opened it. Reload the current version.")
    previous = current_version(db, draft)
    append_version(
        db,
        draft,
        data.subject,
        data.body,
        previous.cta,
        previous.personalization,
        {**previous.context, "human_edited": True},
        "edited",
    )
    db.commit()
    return draft_json(db, draft)


@router.post("/{draft_id}/regenerate")
def regenerate_draft(draft_id: UUID, data: OutreachGenerate, db: Db):
    draft = locked_draft(db, draft_id)
    if draft.prospect_id != data.prospect_id:
        raise HTTPException(422, "Regeneration must use the draft's original prospect")
    if draft.status == "archived":
        raise HTTPException(409, "Archived drafts cannot be regenerated")
    try:
        _, research, result, context = generate_content(db, data)
        draft.research_id, draft.tone, draft.sender_context = research.id, data.tone, data.sender.model_dump()
        append_version(
            db,
            draft,
            result.subject,
            result.full_email,
            result.cta,
            {
                "opening": result.opening,
                "main_body": result.main_body,
                "value_proposition": result.value_proposition,
            },
            context,
            "regenerated",
        )
        db.commit()
        return draft_json(db, draft)
    except AIError as exc:
        raise HTTPException(422, str(exc)) from exc
