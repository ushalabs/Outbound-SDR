from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select

from app.db import Db
from app.models import ActivityLog, ApprovalEvent, Company, DraftVersion, OutreachDraft, Prospect, Research

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])
LOCAL_TIMEZONE = "Asia/Karachi"


@router.get("")
def dashboard_analytics(db: Db, start: date | None = None, end: date | None = None):
    zone = ZoneInfo(LOCAL_TIMEZONE)
    end = end or datetime.now(zone).date()
    start = start or end - timedelta(days=29)
    days = (end - start).days + 1
    if not 1 <= days <= 366:
        raise HTTPException(422, "Choose a date range of 1 to 366 days with start before end")
    lower = datetime.combine(start, time.min, zone).astimezone(UTC)
    upper = datetime.combine(end + timedelta(days=1), time.min, zone).astimezone(UTC)
    cohort = (Prospect.created_at >= lower, Prospect.created_at < upper)
    total = db.scalar(select(func.count()).select_from(Prospect).where(*cohort))
    previous = db.scalar(select(func.count()).select_from(Prospect).where(
        Prospect.created_at >= lower - timedelta(days=days), Prospect.created_at < lower))
    status_rows = db.execute(select(Prospect.status, func.count()).where(*cohort).group_by(Prospect.status)).all()
    status_counts = dict(status_rows)
    researched = db.scalar(select(func.count()).select_from(Prospect).where(*cohort,
        select(Research.id).where(Research.prospect_id == Prospect.id, Research.status == "completed").exists()))
    drafts = dict(db.execute(select(OutreachDraft.status, func.count()).where(
        OutreachDraft.created_at >= lower, OutreachDraft.created_at < upper).group_by(OutreachDraft.status)).all())
    industries = db.execute(select(func.coalesce(Company.industry, "Not classified"), func.count(func.distinct(Company.id)))
        .join(Prospect, Prospect.company_id == Company.id).where(*cohort)
        .group_by(Company.industry).order_by(func.count(func.distinct(Company.id)).desc()).limit(8)).all()
    series = {start + timedelta(days=i): {"date": (start + timedelta(days=i)).isoformat(), "prospects": 0,
        "research": 0, "generated": 0, "approved": 0, "rejected": 0} for i in range(days)}

    def add_daily(column, key, model, *conditions):
        day = func.date(func.timezone(LOCAL_TIMEZONE, column))
        rows = db.execute(select(day, func.count()).select_from(model).where(column >= lower, column < upper,
                         *conditions).group_by(day)).all()
        for bucket, count in rows:
            if bucket in series:
                series[bucket][key] = count

    add_daily(Prospect.created_at, "prospects", Prospect)
    add_daily(Research.finished_at, "research", Research, Research.status == "completed")
    add_daily(ApprovalEvent.created_at, "generated", ApprovalEvent, ApprovalEvent.action.in_(("created", "regenerated")))
    add_daily(ApprovalEvent.created_at, "approved", ApprovalEvent, ApprovalEvent.action == "approved")
    add_daily(ApprovalEvent.created_at, "rejected", ApprovalEvent, ApprovalEvent.action == "rejected")
    turnaround = db.scalar(select(func.avg(func.extract("epoch", ApprovalEvent.created_at - DraftVersion.created_at)) / 60)
        .select_from(ApprovalEvent)
        .join(DraftVersion, DraftVersion.id == ApprovalEvent.version_id).where(ApprovalEvent.action == "approved",
        ApprovalEvent.created_at >= lower, ApprovalEvent.created_at < upper))
    recent = db.scalars(select(ActivityLog).where(ActivityLog.created_at >= lower, ActivityLog.created_at < upper)
                        .order_by(ActivityLog.created_at.desc(), ActivityLog.id).limit(5)).all()
    return {"range": {"start": start, "end": end, "days": days, "timezone": LOCAL_TIMEZONE},
        "totals": {"prospects": total, "researched": researched, "qualified": status_counts.get("qualified", 0),
                   "unqualified": status_counts.get("unqualified", 0), "pending": drafts.get("pending", 0),
                   "approved": drafts.get("approved", 0), "rejected": drafts.get("rejected", 0),
                   "generated": sum(row["generated"] for row in series.values()),
                   "research_runs": sum(row["research"] for row in series.values())},
        "prospect_growth_pct": round((total-previous)/previous*100, 1) if previous else None,
        "previous_prospects": previous, "research_coverage_pct": round(researched/total*100, 1) if total else None,
        "qualification_pct": round(status_counts.get("qualified", 0)/total*100, 1) if total else None,
        "approval_turnaround_minutes": round(float(turnaround), 2) if turnaround is not None else None,
        "daily": list(series.values()), "statuses": [{"name": name, "value": value} for name, value in status_rows],
        "industries": [{"name": name, "value": value} for name, value in industries],
        "recent_activity": [{name: getattr(event, name) for name in
            ("id", "event_type", "entity_type", "entity_id", "details", "created_at")} for event in recent]}
