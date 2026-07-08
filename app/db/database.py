from datetime import datetime

from sqlmodel import Session, select

from app.models.user import User


def find_user_by_email(session: Session, user_email: str) -> User | None:
    statement = select(User).where(User.user_email == user_email)
    return session.exec(statement).first()


def create_user(
    session: Session,
    user_name: str,
    user_email: str,
    password_hash: str,
    created_at: datetime,
) -> User:
    user = User(
        user_name=user_name,
        user_email=user_email,
        password_hash=password_hash,
        created_at=created_at,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
