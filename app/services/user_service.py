from datetime import datetime, timezone
from sqlmodel import Session

from app.db import database
from app.models.user import User


def find_by_email(session: Session, email: str) -> User | None:
    return database.find_user_by_email(session, email)


def create_user(session: Session, user_name: str, email: str, password_hash: str) -> User:
    created_at = datetime.now(timezone.utc)
    return database.create_user(
        session,
        user_name=user_name,
        user_email=email,
        password_hash=password_hash,
        created_at=created_at,
    )
