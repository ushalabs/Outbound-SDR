from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select

from app.db import Db
from app.models import Prospect, Research, ResearchSource
from app.research_schemas import ResearchStart
from app.services.prospects import activity

router = APIRouter(prefix="/api/research", tags=["Research"])


def research_json(job, sources=None):
    result = {name: getattr(job, name) for name in ("id", "company_id", "prospect_id", "status", "stage",
              "findings", "error", "model", "created_at", "updated_at", "started_at", "finished_at", "attempts")}
    result["input_snapshot"] = {key: value for key, value in job.input_snapshot.items() if key != "manual_notes"}
    if sources is not None:
        result["sources"] = [{name: getattr(source, name) for name in
            ("id", "url", "title", "kind", "evidence", "fetched_at")} for source in sources]
    return result


def enqueue(data: ResearchStart, db):
    prospect = db.scalar(select(Prospect).where(Prospect.id == data.prospect_id).with_for_update(of=Prospect))
    if not prospect:
        raise HTTPException(404, "Prospect not found")
    running = db.scalar(select(Research.id).where(Research.prospect_id == prospect.id,
                                                 Research.status.in_(("queued", "running"))))
    if running:
        raise HTTPException(409, "This prospect already has queued or running research")
    if data.manual_notes is not None and len(data.manual_notes.strip()) < 50:
        raise HTTPException(422, "Provide at least 50 characters of useful source notes")
    job = Research(company_id=prospect.company_id, prospect_id=prospect.id, input_snapshot={
        "company_name": prospect.company.name, "website_url": prospect.company.website_url,
        "manual_notes": data.manual_notes, "previous_prospect_status": prospect.status})
    db.add(job)
    db.flush()
    prospect.status = "researching"
    activity(db, "research.queued", "research", job.id)
    db.commit()
    return research_json(job)


@router.post("", status_code=202)
def start_research(data: ResearchStart, db: Db):
    return enqueue(data, db)


@router.get("")
def research_history(db: Db, prospect_id: UUID | None = None, page: int = Query(1, ge=1),
                     page_size: int = Query(20, ge=1, le=100)):
    statement = select(Research)
    if prospect_id:
        statement = statement.where(Research.prospect_id == prospect_id)
    total = db.scalar(select(func.count()).select_from(statement.subquery()))
    records = db.scalars(statement.order_by(Research.created_at.desc()).offset((page-1)*page_size)
                         .limit(page_size)).all()
    return {"items": [research_json(job) for job in records], "total": total, "page": page, "page_size": page_size}


@router.get("/{job_id}")
def research_detail(job_id: UUID, db: Db):
    job = db.get(Research, job_id)
    if not job:
        raise HTTPException(404, "Research run not found")
    sources = db.scalars(select(ResearchSource).where(ResearchSource.research_id == job.id)
                         .order_by(ResearchSource.created_at)).all()
    return research_json(job, sources)


@router.post("/{job_id}/rerun", status_code=202)
def rerun_research(job_id: UUID, db: Db):
    previous = db.get(Research, job_id)
    if not previous or not previous.prospect_id:
        raise HTTPException(404, "Research run or original prospect no longer exists")
    return enqueue(ResearchStart(prospect_id=previous.prospect_id,
                                manual_notes=previous.input_snapshot.get("manual_notes")), db)
