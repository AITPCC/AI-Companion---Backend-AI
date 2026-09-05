from datetime import datetime

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlmodel import Session, select

from app.models.quota import Quota
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

def find_user_by_id(session: Session, user_id: int) -> User | None:
    statement = select(User).where(User.user_id == user_id)
    return session.exec(statement).first()


def update_user_name(session: Session, user: User, user_name: str) -> User:
    user.user_name = user_name
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def upsert_quota_and_increment(
    session: Session,
    actor_kind: str,
    actor_id: str,
    endpoint: str,
    window_start: datetime,
) -> int:
    stmt = pg_insert(Quota.__table__).values(
        actor_kind=actor_kind,
        actor_id=actor_id,
        endpoint=endpoint,
        window_start=window_start,
        request_count=1,
    )
    stmt = stmt.on_conflict_do_update(
        constraint="uq_quota_key",
        set_={"request_count": Quota.__table__.c.request_count + 1},
    ).returning(Quota.__table__.c.request_count)

    result = session.exec(stmt)
    new_count = result.one()[0]
    session.commit()
    return new_count