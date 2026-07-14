from datetime import datetime, timezone
from sqlmodel import Session

from app.db import database
from app.models.user import User
from app.schema.schemas import UserProfile


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


def find_by_id(session: Session, user_id: int) -> User | None:
    return database.find_user_by_id(session, user_id)


def update_user_name(session: Session, user: User, user_name: str) -> User:
    return database.update_user_name(session, user, user_name)


def to_user_profile(user: User) -> UserProfile:
    return UserProfile(
        user_id=user.user_id,
        user_name=user.user_name,
        email=user.user_email,
        created_at=user.created_at,
    )