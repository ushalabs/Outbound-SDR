from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.db import Db
from app.models import Prospect, Research, ResearchChunk, ResearchSource
from app.services.ai import AIError
from app.services.embeddings import embed_research, retrieve

router = APIRouter(prefix="/api", tags=["Semantic research"])


class SemanticQuery(BaseModel):
    query: str = Field(min_length=3, max_length=1000)
    prospect_id: UUID | None = None
    company_id: UUID | None = None
    limit: int = Field(default=5, ge=1, le=20)


@router.post("/research/{research_id}/embeddings")
def generate_embeddings(research_id: UUID, db: Db):
    research = db.get(Research, research_id)
    if not research:
        raise HTTPException(404, "Research not found")
    try:
        return embed_research(db, research)
    except AIError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/research/{research_id}/embeddings")
def embedding_state(research_id: UUID, db: Db):
    if not db.get(Research, research_id):
        raise HTTPException(404, "Research not found")
    rows = db.scalars(
        select(ResearchChunk).join(ResearchSource).where(ResearchSource.research_id == research_id)
    ).all()
    return {
        "total": len(rows),
        "completed": sum(c.embedding_status == "completed" for c in rows),
        "failed": sum(c.embedding_status == "failed" for c in rows),
        "stale": sum(c.embedding_status == "stale" for c in rows),
        "models": sorted({c.embedding_model for c in rows if c.embedding_model}),
        "errors": list({c.embedding_error for c in rows if c.embedding_error}),
    }


@router.post("/semantic/search")
def semantic_search(data: SemanticQuery, db: Db):
    company_id = data.company_id
    if data.prospect_id:
        prospect = db.get(Prospect, data.prospect_id)
        if not prospect:
            raise HTTPException(404, "Prospect not found")
        if company_id and company_id != prospect.company_id:
            raise HTTPException(422, "Company and prospect filters must refer to the same company")
        company_id = prospect.company_id
    try:
        results = retrieve(db, data.query, company_id, data.limit)
        return {
            "items": results,
            "message": None
            if results
            else "No current embeddings match this scope. Complete research and generate embeddings first.",
        }
    except AIError as exc:
        raise HTTPException(503, str(exc)) from exc
