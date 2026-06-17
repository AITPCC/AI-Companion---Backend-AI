from datetime import datetime, timezone
from typing import Any

from app.db import database


def find_by_email(email: str) -> dict[str, Any] | None:
    return database.find_user_by_email(email)


def create_user(user_name: str, email: str, password_hash: str) -> dict[str, Any]:
    created_at = datetime.now(timezone.utc)
    return database.create_user(
        user_name=user_name,
        user_email=email,
        password_hash=password_hash,
        created_at=created_at,
    )
