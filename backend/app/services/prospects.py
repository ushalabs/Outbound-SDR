import csv
import hashlib
import io
from uuid import UUID

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import ActivityLog, Company, Prospect
from app.schemas import ProspectInput, domain_of


def activity(db: Session, event: str, kind: str, entity_id: UUID | None, **details):
    # Only callers' small controlled fields, never prompts, credentials or raw records.
    db.add(ActivityLog(event_type=event, entity_type=kind, entity_id=entity_id, details=details))


def duplicate(db: Session, data: ProspectInput, exclude: UUID | None = None):
    tests = [Prospect.identity_key == data.identity_key()]
    if data.email:
        tests.append(Prospect.email == str(data.email))
    statement = select(Prospect).where(or_(*tests))
    if exclude:
        statement = statement.where(Prospect.id != exclude)
    return db.scalar(statement)


def save_prospect(db: Session, data: ProspectInput, existing: Prospect | None = None) -> Prospect:
    if duplicate(db, data, existing.id if existing else None):
        raise HTTPException(409, "This company/contact or email already exists")
    domain = domain_of(data.website_url)
    company = db.scalar(select(Company).where(Company.domain == domain))
    if not company:
        company = Company(
            name=data.company_name, domain=domain, website_url=data.website_url, industry=data.industry
        )
        try:
            with db.begin_nested():
                db.add(company)
                db.flush()
        except IntegrityError:
            company = db.scalar(select(Company).where(Company.domain == domain))
            if not company:
                raise HTTPException(409, "Company changed during creation. Retry the request.") from None
    elif existing and existing.company_id == company.id:
        company.name, company.website_url, company.industry = (
            data.company_name,
            data.website_url,
            data.industry,
        )
    prospect = existing or Prospect()
    prospect.company = company
    for key, value in data.model_dump(exclude={"company_name", "website_url", "industry"}).items():
        setattr(prospect, key, str(value) if key == "email" and value else value)
    prospect.identity_key = data.identity_key()
    db.add(prospect)
    try:
        db.flush()
    except IntegrityError as exc:
        raise HTTPException(409, "This company/contact or email already exists") from exc
    activity(db, "prospect.updated" if existing else "prospect.created", "prospect", prospect.id)
    return prospect


ALIASES = {
    "company": "company_name",
    "company name": "company_name",
    "website": "website_url",
    "domain": "website_url",
    "name": "full_name",
    "full name": "full_name",
    "title": "job_title",
    "job title": "job_title",
    "linkedin": "linkedin_url",
}


def csv_columns(text: str):
    if len(text.encode("utf-8")) > 2_000_000:
        raise HTTPException(413, "CSV exceeds the 2 MB limit")
    try:
        headers = csv.DictReader(io.StringIO(text.lstrip("\ufeff")), strict=True).fieldnames
    except csv.Error as exc:
        raise HTTPException(422, "CSV header could not be parsed") from exc
    if not headers or len(headers) > 30 or len(set(headers)) != len(headers):
        raise HTTPException(422, "CSV needs unique headers and at most 30 columns")
    fields = set(ProspectInput.model_fields)
    return {
        "headers": headers,
        "mapping": {
            header: target if target in fields else "ignore"
            for header in headers
            for target in [ALIASES.get(header.strip().lower(), header.strip().lower())]
        },
    }


def preview_csv(db: Session, text: str, mapping: dict[str, str]):
    columns = csv_columns(text)
    headers = columns["headers"]
    reader = csv.DictReader(io.StringIO(text.lstrip("\ufeff")), strict=True)
    fields = set(ProspectInput.model_fields)
    resolved = {
        header: mapping.get(header, ALIASES.get(header.strip().lower(), header.strip().lower()))
        for header in headers
    }
    targets = [target for target in resolved.values() if target in fields]
    if len(targets) != len(set(targets)):
        raise HTTPException(422, "Map each target field from only one CSV column")
    if not {"company_name", "website_url"}.issubset(set(resolved.values())):
        raise HTTPException(422, "Map columns for company_name and website_url")
    staged, rows, errors, seen, duplicates = [], [], [], set(), 0
    try:
        for number, raw in enumerate(reader, start=2):
            if number > 1001:
                raise HTTPException(413, "CSV exceeds the 1,000-row limit")
            if None in raw or any(value is None for value in raw.values()):
                errors.append(
                    {"row": number, "message": "Row has a different number of columns than the header"}
                )
                continue
            values = {
                resolved[header]: value
                for header, value in raw.items()
                if resolved[header] in fields and value.strip()
            }
            values["source"] = "csv"
            try:
                data = ProspectInput.model_validate(values)
                staged.append((number, data))
            except ValidationError as exc:
                errors.append(
                    {
                        "row": number,
                        "message": "; ".join(
                            ".".join(str(v) for v in error["loc"]) + ": " + error["msg"]
                            for error in exc.errors()
                        ),
                    }
                )
    except csv.Error as exc:
        raise HTTPException(422, "CSV could not be parsed. Check quoting and delimiters.") from exc
    if staged:
        keys = [data.identity_key() for _, data in staged]
        emails = [str(data.email) for _, data in staged if data.email]
        existing = db.execute(
            select(Prospect.identity_key, Prospect.email).where(
                or_(Prospect.identity_key.in_(keys), Prospect.email.in_(emails))
            )
        ).all()
        for key, email in existing:
            seen.add(key)
            if email:
                seen.add("email:" + email)
    for number, data in staged:
        key = data.identity_key()
        email_key = "email:" + str(data.email) if data.email else key
        is_duplicate = key in seen or email_key in seen
        seen.update((key, email_key))
        duplicates += int(is_duplicate)
        rows.append({"row": number, "duplicate": is_duplicate, "data": data.model_dump(mode="json")})
    return {
        "headers": headers,
        "mapping": resolved,
        "rows": rows,
        "errors": errors,
        "duplicates": duplicates,
        "total_rows": len(rows) + len(errors),
        "file_hash": hashlib.sha256(text.encode()).hexdigest(),
    }
