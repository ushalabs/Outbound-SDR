import math
from uuid import UUID

import httpx
from google.genai import errors, types
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Company, Research, ResearchChunk, ResearchSource
from app.services.ai import AIError, client
from app.services.prospects import activity


def embedding_model():
    # This text model was confirmed by live models.list; the provider is checked before every batch.
    return get_settings().embedding_model or "gemini-embedding-001"


def embed(texts: list[str], query: bool = False) -> list[list[float]]:
    settings = get_settings()
    if settings.embedding_dimensions != 768:
        raise AIError("EMBEDDING_DIMENSIONS must be 768 for the current database migration")
    try:
        with client() as provider:
            model = provider.models.get(model=embedding_model())
            if "embedContent" not in (model.supported_actions or []):
                raise AIError("EMBEDDING_MODEL does not support embeddings")
            response = provider.models.embed_content(
                model=embedding_model(),
                contents=texts,
                config=types.EmbedContentConfig(
                    output_dimensionality=768, task_type="RETRIEVAL_QUERY" if query else "RETRIEVAL_DOCUMENT"
                ),
            )
            vectors = [item.values for item in (response.embeddings or [])]
            if len(vectors) != len(texts):
                raise AIError("Provider returned an unexpected number of embeddings")
            normalized = []
            for vector in vectors:
                if vector is None or len(vector) != 768 or any(not math.isfinite(v) for v in vector):
                    raise AIError("Provider returned invalid embedding dimensions or values")
                norm = math.sqrt(sum(v * v for v in vector))
                if norm == 0:
                    raise AIError("Provider returned an empty embedding vector")
                normalized.append([v / norm for v in vector])
            return normalized
    except errors.APIError as exc:
        raise AIError(
            f"Embedding API failed (HTTP {exc.code}, {exc.status}); no synthetic vectors were stored"
        ) from exc
    except (TimeoutError, OSError, httpx.HTTPError) as exc:
        raise AIError("Embedding API network request failed") from exc


def latest_research(db: Session, company_id: UUID):
    return db.scalar(
        select(Research)
        .where(Research.company_id == company_id, Research.status == "completed")
        .order_by(Research.created_at.desc(), Research.id)
        .limit(1)
    )


def embed_research(db: Session, research: Research):
    if research.status != "completed":
        raise AIError("Complete valid research before generating embeddings")
    latest = latest_research(db, research.company_id)
    if not latest or latest.id != research.id:
        raise AIError("Only the latest completed company research can be embedded")
    chunks = db.scalars(
        select(ResearchChunk)
        .join(ResearchSource)
        .where(ResearchSource.research_id == research.id)
        .order_by(ResearchChunk.created_at, ResearchChunk.id)
    ).all()
    if not chunks:
        raise AIError("This research contains no evidence chunks")
    # Clear first; a failed re-embedding must never advertise old vectors as current.
    for chunk in chunks:
        chunk.embedding, chunk.embedding_status, chunk.embedding_error = None, "missing", None
    db.commit()
    try:
        vectors = embed([chunk.text for chunk in chunks])
        for chunk, vector in zip(chunks, vectors, strict=True):
            chunk.embedding, chunk.embedding_status = vector, "completed"
            chunk.embedding_model = embedding_model()
        activity(
            db, "research.embedded", "research", research.id, chunks=len(chunks), model=embedding_model()
        )
        db.commit()
    except AIError as exc:
        for chunk in chunks:
            chunk.embedding, chunk.embedding_status, chunk.embedding_error = None, "failed", str(exc)
        db.commit()
        raise
    return {
        "research_id": research.id,
        "embedded_chunks": len(chunks),
        "dimensions": 768,
        "model": embedding_model(),
        "index_policy": "Exact cosine scan; consider HNSW after 1,000 current chunks.",
    }


def retrieve(
    db: Session, query: str, company_id: UUID | None = None, limit: int = 5, research_id: UUID | None = None
):
    # Only latest completed research per company; stale or mismatched-model vectors are excluded.
    ranked = (
        select(
            Research.id,
            func.row_number()
            .over(partition_by=Research.company_id, order_by=(Research.created_at.desc(), Research.id))
            .label("position"),
        )
        .where(Research.status == "completed")
        .subquery()
    )
    newest = select(ranked.c.id).where(ranked.c.position == 1)
    statement = select(ResearchChunk, ResearchSource, Research, Company).select_from(ResearchChunk)
    statement = statement.join(ResearchSource, ResearchSource.id == ResearchChunk.source_id)
    statement = statement.join(Research, Research.id == ResearchSource.research_id)
    statement = statement.join(Company, Company.id == Research.company_id).where(
        Research.id.in_(newest),
        ResearchChunk.embedding_status == "completed",
        ResearchChunk.embedding.is_not(None),
        ResearchChunk.embedding_model == embedding_model(),
    )
    if company_id:
        statement = statement.where(Research.company_id == company_id)
    if research_id:
        statement = statement.where(Research.id == research_id)
    if not db.scalar(select(func.count()).select_from(statement.subquery())):
        return []
    vector = embed([query], query=True)[0]
    distance = ResearchChunk.embedding.cosine_distance(vector)
    rows = db.execute(statement.add_columns(distance.label("distance")).order_by(distance).limit(limit)).all()
    return [
        {
            "chunk_id": chunk.id,
            "text": chunk.text,
            "source_id": source.id,
            "source_url": source.url,
            "source_kind": source.kind,
            "source_title": source.title,
            "research_id": research.id,
            "company_id": company.id,
            "company_name": company.name,
            "similarity": round(1 - float(score), 4),
        }
        for chunk, source, research, company, score in rows
    ]
