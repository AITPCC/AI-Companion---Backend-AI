"""Run hourly in a Cloud Run job: uv run python -m app.jobs.cleanup_quotas."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlmodel import Session

from app.core.config import get_settings
from app.db.engine import engine
from app.models.quota import Quota


def cleanup_batch(session: Session, cutoff: datetime, batch_size: int = 1000) -> int:
    old_ids = (
        select(Quota.quota_id)
        .where(Quota.window_start < cutoff)
        .order_by(Quota.window_start)
        .limit(batch_size)
        .with_for_update(skip_locked=True)
    )
    result = session.execute(delete(Quota).where(Quota.quota_id.in_(old_ids)))
    session.commit()
    return result.rowcount


def main():
    settings = get_settings()
    longest_window = max(
        settings.chat_window_seconds,
        settings.login_window_seconds,
        settings.register_window_seconds,
    )
    cutoff = datetime.now(timezone.utc) - timedelta(
        seconds=longest_window + settings.quota_retention_seconds
    )
    # Bound each execution; repeated scheduled runs drain a backlog.
    with Session(engine) as session:
        for _ in range(100):
            if cleanup_batch(session, cutoff) < 1000:
                break


if __name__ == "__main__":
    main()
