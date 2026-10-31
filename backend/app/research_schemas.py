from typing import Generic, Literal, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field


class EvidenceReference(BaseModel):
    source_id: str
    quote: str = Field(min_length=10, max_length=1000)


class GroundedStatement(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    references: list[EvidenceReference] = Field(min_length=1, max_length=4)


class EvidenceSelection(BaseModel):
    source_id: str
    passage_id: int = Field(ge=0)


class SelectedStatement(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    references: list[EvidenceSelection] = Field(min_length=1, max_length=4)


Statement = TypeVar("Statement")


class CompanyFindings(BaseModel, Generic[Statement]):
    overview: Statement
    industry: Statement | None = None
    products_services: list[Statement] = Field(max_length=8)
    supported_facts: list[Statement] = Field(min_length=1, max_length=10)
    potential_challenges_hypotheses: list[str] = Field(max_length=5)
    qualification: Literal["qualified", "unqualified", "insufficient_information"]
    qualification_reasoning: str = Field(max_length=2000)
    personalization_opportunities: list[Statement] = Field(max_length=5)
    suggested_outreach_angle_hypothesis: str = Field(max_length=2000)
    confidence: Literal["low", "medium", "high"]
    missing_information: list[str] = Field(max_length=10)


class ResearchFindings(CompanyFindings[GroundedStatement]):
    pass


class ResearchAnalysis(CompanyFindings[SelectedStatement]):
    pass


class ResearchStart(BaseModel):
    prospect_id: UUID
    manual_notes: str | None = Field(default=None, max_length=20000)
