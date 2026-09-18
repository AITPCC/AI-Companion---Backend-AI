from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session

from app.db import database
from app.db.session import SessionDep
from app.models.user import User
from app.schema.schemas import UserProfile
from app.services import auth_service


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


def delete_user(session: Session, user: User) -> None:
    database.delete_user(session, user)


def to_user_profile(user: User) -> UserProfile:
    return UserProfile(
        user_id=user.user_id,
        user_name=user.user_name,
        email=user.user_email,
        created_at=user.created_at,
    )


def get_current_user(
    session: SessionDep,
    credentials: HTTPAuthorizationCredentials = Depends(auth_service.http_bearer_scheme),
) -> User:
    payload = auth_service.decode_access_token(credentials.credentials)
    user_id = payload.get("user_id")
    user = find_by_id(session, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user