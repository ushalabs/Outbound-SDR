import hashlib
from datetime import datetime
from typing import Literal
from urllib.parse import urlsplit, urlunsplit
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

ProspectStatus = Literal["new", "researching", "researched", "qualified", "unqualified"]


def normalize_url(value: str) -> str:
    value = value.strip()
    if "://" not in value:
        value = "https://" + value
    parsed = urlsplit(value)
    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Use a public HTTP or HTTPS URL without credentials")
    host = parsed.hostname.encode("idna").decode().lower().rstrip(".")
    if parsed.port not in (None, 80, 443) or ":" in host:
        raise ValueError("Only standard public website ports are supported")
    return urlunsplit((parsed.scheme, host, parsed.path or "/", parsed.query, ""))


def domain_of(url: str) -> str:
    host = urlsplit(normalize_url(url)).hostname
    return host.removeprefix("www.")


class ProspectInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    company_name: str = Field(min_length=1, max_length=200)
    website_url: str = Field(min_length=1, max_length=2048)
    industry: str | None = Field(default=None, max_length=160)
    full_name: str | None = Field(default=None, max_length=200)
    email: EmailStr | None = None
    job_title: str | None = Field(default=None, max_length=200)
    location: str | None = Field(default=None, max_length=200)
    linkedin_url: str | None = Field(default=None, max_length=2048)
    source: str = Field(default="manual", max_length=80)
    source_url: str | None = Field(default=None, max_length=2048)
    notes: str | None = Field(default=None, max_length=10000)
    status: ProspectStatus = "new"
    do_not_contact: bool = False

    @field_validator(
        "email",
        "industry",
        "full_name",
        "job_title",
        "location",
        "linkedin_url",
        "source_url",
        "notes",
        mode="before",
    )
    @classmethod
    def empty_as_none(cls, value):
        return None if isinstance(value, str) and not value.strip() else value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        return str(value).lower() if value else None

    @field_validator("website_url", "linkedin_url", "source_url")
    @classmethod
    def normalize_website(cls, value):
        return normalize_url(value) if value else value

    def identity_key(self) -> str:
        # Email stays separately unique; identity remains stable when an email is supplied later.
        parts = (
            domain_of(self.website_url),
            (self.full_name or "").casefold(),
            (self.job_title or "").casefold(),
        )
        return hashlib.sha256("|".join(parts).encode()).hexdigest()


class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    domain: str
    website_url: str
    industry: str | None
    created_at: datetime


class ProspectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    company: CompanyOut
    full_name: str | None
    email: str | None
    job_title: str | None
    location: str | None
    linkedin_url: str | None
    source: str
    source_url: str | None
    notes: str | None
    status: ProspectStatus
    do_not_contact: bool
    created_at: datetime
    updated_at: datetime


class BulkProspects(BaseModel):
    ids: list[UUID] = Field(min_length=1, max_length=100)
    action: Literal["status", "do_not_contact", "delete"]
    status: ProspectStatus | None = None
    confirm: bool = False


class CsvPreview(BaseModel):
    csv_text: str = Field(max_length=2_000_000)
    mapping: dict[str, str] = Field(default_factory=dict, max_length=20)


class CsvImport(CsvPreview):
    filename: str = Field(default="import.csv", min_length=1, max_length=200)
    confirm: Literal[True]


class DiscoveryInput(BaseModel):
    urls: list[str] = Field(min_length=1, max_length=3)


class DiscoveryImport(BaseModel):
    prospects: list[ProspectInput] = Field(min_length=1, max_length=20)
    confirm: Literal[True]
