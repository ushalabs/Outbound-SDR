from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.research_schemas import EvidenceReference


class SenderContext(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(min_length=1, max_length=120)
    company: str = Field(min_length=1, max_length=200)
    value_proposition: str = Field(min_length=10, max_length=2000)


class OutreachGenerate(BaseModel):
    prospect_id: UUID
    tone: Literal["professional", "concise", "friendly"] = "professional"
    sender: SenderContext


class OutreachContent(BaseModel):
    subject: str = Field(min_length=1, max_length=300)
    opening: str = Field(min_length=1, max_length=2000)
    main_body: str = Field(min_length=1, max_length=4000)
    value_proposition: str = Field(min_length=1, max_length=2000)
    cta: str = Field(min_length=1, max_length=1000)
    full_email: str = Field(min_length=1, max_length=10000)
    referenced_evidence: list[EvidenceReference] = Field(min_length=1, max_length=8)


class DraftEdit(BaseModel):
    subject: str = Field(min_length=1, max_length=300)
    body: str = Field(min_length=1, max_length=10000)
    expected_version: int = Field(ge=1)
