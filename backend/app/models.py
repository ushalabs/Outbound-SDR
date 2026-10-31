import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    metadata = MetaData(schema="sdr", naming_convention={
        "ix": "ix_%(table_name)s_%(column_0_name)s", "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s", "fk": "fk_%(table_name)s_%(column_0_name)s",
        "pk": "pk_%(table_name)s",
    })


class Record:
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class Updated:
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                               onupdate=func.now())


class Company(Record, Updated, Base):
    __tablename__ = "companies"
    name: Mapped[str] = mapped_column(String(200))
    domain: Mapped[str] = mapped_column(String(253), unique=True)
    website_url: Mapped[str] = mapped_column(Text)
    industry: Mapped[str | None] = mapped_column(String(160), index=True)


class Prospect(Record, Updated, Base):
    __tablename__ = "prospects"
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sdr.companies.id"), index=True)
    company: Mapped[Company] = relationship(lazy="joined")
    full_name: Mapped[str | None] = mapped_column(String(200))
    email: Mapped[str | None] = mapped_column(String(320), unique=True)
    identity_key: Mapped[str] = mapped_column(String(64), unique=True)
    job_title: Mapped[str | None] = mapped_column(String(200))
    location: Mapped[str | None] = mapped_column(String(200))
    linkedin_url: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(80), default="manual")
    source_url: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="new", index=True)
    do_not_contact: Mapped[bool] = mapped_column(Boolean, default=False)
    __table_args__ = (CheckConstraint("status IN ('new','researching','researched','qualified','unqualified')",
                                     name="status"), Index("ix_prospects_name", "full_name"))


class Research(Record, Updated, Base):
    __tablename__ = "research"
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sdr.companies.id"), index=True)
    prospect_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("sdr.prospects.id", ondelete="SET NULL"),
                                                        index=True)
    status: Mapped[str] = mapped_column(String(32), default="queued", index=True)
    stage: Mapped[str] = mapped_column(String(100), default="Queued")
    input_snapshot: Mapped[dict] = mapped_column(JSONB, default=dict)
    findings: Mapped[dict | None] = mapped_column(JSONB)
    error: Mapped[str | None] = mapped_column(Text)
    model: Mapped[str | None] = mapped_column(String(120))
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (CheckConstraint("status IN ('queued','running','completed','failed')", name="status"),)


class ResearchSource(Record, Base):
    __tablename__ = "research_sources"
    research_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sdr.research.id", ondelete="CASCADE"), index=True)
    url: Mapped[str | None] = mapped_column(Text)
    title: Mapped[str] = mapped_column(String(300))
    kind: Mapped[str] = mapped_column(String(32), default="website")
    evidence: Mapped[str] = mapped_column(Text)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ResearchChunk(Record, Base):
    __tablename__ = "research_chunks"
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sdr.research_sources.id", ondelete="CASCADE"),
                                               index=True)
    text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(768))
    embedding_model: Mapped[str | None] = mapped_column(String(120))
    embedding_status: Mapped[str] = mapped_column(String(32), default="missing")
    embedding_error: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (CheckConstraint("embedding_status IN ('missing','completed','failed','stale')",
                                     name="embedding_status"),)


class OutreachDraft(Record, Updated, Base):
    __tablename__ = "outreach_drafts"
    prospect_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sdr.prospects.id", ondelete="CASCADE"), index=True)
    research_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sdr.research.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    tone: Mapped[str] = mapped_column(String(32), default="professional")
    current_version: Mapped[int] = mapped_column(Integer, default=1)
    sender_context: Mapped[dict] = mapped_column(JSONB, default=dict)
    __table_args__ = (CheckConstraint("status IN ('pending','approved','rejected','archived')", name="status"),
                      CheckConstraint("tone IN ('professional','concise','friendly')", name="tone"),
                      CheckConstraint("current_version > 0", name="version"))


class DraftVersion(Record, Base):
    __tablename__ = "draft_versions"
    draft_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sdr.outreach_drafts.id", ondelete="CASCADE"), index=True)
    version: Mapped[int] = mapped_column(Integer)
    subject: Mapped[str] = mapped_column(String(300))
    body: Mapped[str] = mapped_column(Text)
    personalization: Mapped[dict] = mapped_column(JSONB, default=dict)
    cta: Mapped[str] = mapped_column(Text)
    context: Mapped[dict] = mapped_column(JSONB, default=dict)
    __table_args__ = (UniqueConstraint("draft_id", "version"), CheckConstraint("version > 0", name="version"))


class ApprovalEvent(Record, Base):
    __tablename__ = "approval_events"
    draft_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sdr.outreach_drafts.id", ondelete="CASCADE"), index=True)
    version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sdr.draft_versions.id", ondelete="CASCADE"))
    action: Mapped[str] = mapped_column(String(32))
    note: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (CheckConstraint("action IN ('created','edited','regenerated','approved','rejected',"
                                     "'archived','reopened')", name="action"),)


class ActivityLog(Record, Base):
    __tablename__ = "activity_logs"
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    entity_type: Mapped[str] = mapped_column(String(40))
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), index=True)
    details: Mapped[dict] = mapped_column(JSONB, default=dict)


class ImportJob(Record, Base):
    __tablename__ = "import_jobs"
    filename: Mapped[str] = mapped_column(String(200))
    file_hash: Mapped[str] = mapped_column(String(64))
    total_rows: Mapped[int] = mapped_column(Integer)
    imported_rows: Mapped[int] = mapped_column(Integer, default=0)
    duplicates: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[list] = mapped_column(JSONB, default=list)
    __table_args__ = (CheckConstraint("total_rows >= 0 AND imported_rows >= 0 AND duplicates >= 0",
                                     name="row_counts"),)
