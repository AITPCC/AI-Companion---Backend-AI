from datetime import datetime, timezone

from sqlmodel import Session

from app.db import database


def get_window_start(window_seconds: int) -> datetime:
    now = datetime.now(timezone.utc)
    epoch_seconds = int(now.timestamp())
    aligned_seconds = (epoch_seconds // window_seconds) * window_seconds
    return datetime.fromtimestamp(aligned_seconds, tz=timezone.utc)


def check_and_increment(
    session: Session,
    actor_kind: str,
    actor_id: str,
    endpoint: str,
    limit: int,
    window_seconds: int,
) -> bool:
    window_start = get_window_start(window_seconds)
    new_count = database.upsert_quota_and_increment(
        session, actor_kind, actor_id, endpoint, window_start
    )
    return new_count <= limit
