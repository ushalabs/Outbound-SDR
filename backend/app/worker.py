"""Single local worker; queued/running state is durable in PostgreSQL."""
import logging
import signal
import threading
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.db import SessionLocal
from app.logging_config import configure_logging
from app.models import Prospect, Research
from app.services.prospects import activity
from app.services.research import run_research

stop = threading.Event()


def main():
    configure_logging()
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    while not stop.is_set():
        try:
            with SessionLocal() as db:
                stale = db.scalars(select(Research).where(Research.status == "running",
                    Research.started_at < datetime.now(UTC) - timedelta(minutes=10)).with_for_update(skip_locked=True)).all()
                for job in stale:
                    job.status, job.stage = "failed", "Interrupted run"
                    job.error, job.finished_at = "Worker was interrupted or exceeded its time budget. Re-run explicitly.", datetime.now(UTC)
                    prospect = db.get(Prospect, job.prospect_id) if job.prospect_id else None
                    if prospect and prospect.status == "researching":
                        prospect.status = job.input_snapshot.get("previous_prospect_status", "new")
                    activity(db, "research.interrupted", "research", job.id)
                db.commit()
                job = db.scalar(select(Research).where(Research.status == "queued").order_by(Research.created_at)
                                .with_for_update(skip_locked=True).limit(1))
                if job:
                    job.status, job.started_at = "running", datetime.now(UTC)
                    db.commit()
                    run_research(db, job)
        except SQLAlchemyError:
            logging.getLogger(__name__).error("Worker database unavailable; queued work will retry")
        except Exception:  # noqa: BLE001 -- unexpected failures are isolated without logging input
            # Unexpected worker errors must not cause jobs to appear completed or log sensitive input.
            logging.getLogger(__name__).error("Worker encountered an unexpected error; interrupted runs recover after timeout")
        stop.wait(2)


if __name__ == "__main__":
    main()
