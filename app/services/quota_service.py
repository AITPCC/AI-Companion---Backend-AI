"""Simple fixed-window quotas backed by PostgreSQL."""

from datetime import datetime, timezone
from hashlib import sha256

from sqlmodel import Session

from app.db import database


def hash_key(*parts: str) -> str:
    """Create a fixed-length key without storing an email address in plain text."""
    return sha256("\0".join(parts).encode()).hexdigest()


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
    return database.upsert_quota_and_increment(
        session, actor_kind, actor_id, endpoint, window_start, limit
    )
