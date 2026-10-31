from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import asc, desc, func, or_, select

from app.db import Db
from app.models import Company, ImportJob, Prospect
from app.schemas import (
    BulkProspects,
    CsvImport,
    CsvPreview,
    DiscoveryImport,
    DiscoveryInput,
    ProspectInput,
    ProspectOut,
    ProspectStatus,
    domain_of,
)
from app.services.fetching import FetchError, fetch_page
from app.services.prospects import activity, csv_columns, preview_csv, save_prospect

router = APIRouter(prefix="/api", tags=["Prospects"])


@router.get("/prospects")
def list_prospects(
    db: Db,
    search: str = Query("", max_length=200),
    status: ProspectStatus | None = None,
    company_id: UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort: str = Query("created_at"),
    direction: str = Query("desc", pattern="^(asc|desc)$"),
):
    statement = select(Prospect).join(Company)
    if search:
        term = "%" + search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        statement = statement.where(
            or_(
                *[
                    column.ilike(term, escape="\\")
                    for column in (Prospect.full_name, Prospect.email, Company.name, Company.domain)
                ]
            )
        )
    if status:
        statement = statement.where(Prospect.status == status)
    if company_id:
        statement = statement.where(Prospect.company_id == company_id)
    order = {
        "created_at": Prospect.created_at,
        "full_name": Prospect.full_name,
        "company": Company.name,
        "status": Prospect.status,
    }.get(sort)
    if order is None:
        raise HTTPException(422, "Sort by created_at, full_name, company or status")
    total = db.scalar(select(func.count()).select_from(statement.subquery()))
    records = db.scalars(
        statement.order_by((asc if direction == "asc" else desc)(order), Prospect.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return {
        "items": [ProspectOut.model_validate(item) for item in records],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/prospects", response_model=ProspectOut, status_code=201)
def create_prospect(data: ProspectInput, db: Db):
    prospect = save_prospect(db, data)
    db.commit()
    return prospect


@router.post("/prospects/bulk")
def bulk_prospects(data: BulkProspects, db: Db):
    if data.action == "delete" and not data.confirm:
        raise HTTPException(422, "Explicit deletion confirmation is required")
    if data.action == "status" and data.status is None:
        raise HTTPException(422, "A target status is required")
    records = db.scalars(select(Prospect).where(Prospect.id.in_(data.ids))).all()
    if len(records) != len(set(data.ids)):
        raise HTTPException(404, "One or more selected prospects no longer exist")
    for prospect in records:
        if data.action == "delete":
            db.delete(prospect)
        elif data.action == "status":
            prospect.status = data.status
        else:
            prospect.do_not_contact = True
        activity(db, f"prospect.bulk_{data.action}", "prospect", prospect.id)
    db.commit()
    return {"updated": len(records)}


def find_prospect(db, prospect_id):
    prospect = db.get(Prospect, prospect_id)
    if not prospect:
        raise HTTPException(404, "Prospect not found")
    return prospect


@router.get("/prospects/{prospect_id}", response_model=ProspectOut)
def get_prospect(prospect_id: UUID, db: Db):
    return find_prospect(db, prospect_id)


@router.patch("/prospects/{prospect_id}", response_model=ProspectOut)
def update_prospect(prospect_id: UUID, data: ProspectInput, db: Db):
    prospect = save_prospect(db, data, find_prospect(db, prospect_id))
    db.commit()
    return prospect


@router.delete("/prospects/{prospect_id}", status_code=204)
def delete_prospect(prospect_id: UUID, db: Db, confirm: bool = False):
    if not confirm:
        raise HTTPException(422, "Explicit deletion confirmation is required")
    prospect = find_prospect(db, prospect_id)
    activity(db, "prospect.deleted", "prospect", prospect.id)
    db.delete(prospect)
    db.commit()


@router.get("/companies/{company_id}")
def company_detail(company_id: UUID, db: Db):
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(404, "Company not found")
    contacts = db.scalars(
        select(Prospect).where(Prospect.company_id == company_id).order_by(Prospect.created_at)
    ).all()
    return {
        "company": {
            "id": company.id,
            "name": company.name,
            "domain": company.domain,
            "website_url": company.website_url,
            "industry": company.industry,
        },
        "prospects": [ProspectOut.model_validate(item) for item in contacts],
    }


@router.post("/imports/preview")
def import_preview(data: CsvPreview, db: Db):
    return preview_csv(db, data.csv_text, data.mapping)


@router.post("/imports/columns")
def import_columns(data: CsvPreview):
    return csv_columns(data.csv_text)


@router.post("/imports/csv", status_code=201)
def import_csv(data: CsvImport, db: Db):
    preview = preview_csv(db, data.csv_text, data.mapping)
    imported, duplicates, errors = 0, preview["duplicates"], list(preview["errors"])
    for row in preview["rows"]:
        if row["duplicate"]:
            continue
        try:
            with db.begin_nested():
                save_prospect(db, ProspectInput.model_validate(row["data"]))
            imported += 1
        except HTTPException as exc:
            if exc.status_code == 409:
                duplicates += 1
            else:
                raise
    job = ImportJob(
        filename=data.filename,
        file_hash=preview["file_hash"],
        total_rows=preview["total_rows"],
        imported_rows=imported,
        duplicates=duplicates,
        errors=errors,
    )
    db.add(job)
    db.flush()
    activity(
        db, "import.completed", "import", job.id, imported=imported, duplicates=duplicates, errors=len(errors)
    )
    db.commit()
    return {
        "id": job.id,
        "total_rows": job.total_rows,
        "imported_rows": imported,
        "duplicates": duplicates,
        "errors": errors,
    }


@router.get("/imports")
def import_history(db: Db):
    records = db.scalars(select(ImportJob).order_by(ImportJob.created_at.desc()).limit(30)).all()
    return [
        {
            "id": row.id,
            "filename": row.filename,
            "total_rows": row.total_rows,
            "imported_rows": row.imported_rows,
            "duplicates": row.duplicates,
            "errors": row.errors,
            "created_at": row.created_at,
        }
        for row in records
    ]


@router.post("/discovery/preview")
def discovery(data: DiscoveryInput):
    results, errors = [], []
    for url in dict.fromkeys(data.urls):
        if len(results) >= 20:
            break
        try:
            page = fetch_page(url)
            if page.companies:
                for candidate in page.companies[: 20 - len(results)]:
                    if any(
                        domain_of(row["website_url"]) == domain_of(candidate["website_url"])
                        for row in results
                    ):
                        continue
                    results.append(
                        {
                            **candidate,
                            "source": "public_website",
                            "source_url": page.url,
                            "title": page.title,
                            "name_source": "explicit structured organization metadata",
                        }
                    )
                continue
            results.append(
                {
                    "company_name": page.company_name or page.title[:200],
                    "website_url": page.url,
                    "source": "public_website",
                    "source_url": page.url,
                    "evidence": page.text[:2000],
                    "title": page.title,
                    "name_source": "website metadata"
                    if page.company_name
                    else "page title; confirm company name",
                }
            )
            if len(results) >= 20:
                break
        except (FetchError, ValueError) as exc:
            errors.append({"url": url, "message": str(exc)})
    return {
        "results": results,
        "errors": errors,
        "limitation": "Up to 20 company candidates from supplied public URLs. Structured directory listings are supported; no broad search or personal-contact harvesting.",
    }


@router.post("/discovery/import", status_code=201)
def import_discovery(data: DiscoveryImport, db: Db):
    records = [save_prospect(db, prospect) for prospect in data.prospects]
    db.commit()
    return {"items": [ProspectOut.model_validate(item) for item in records], "imported_rows": len(records)}
