from datetime import datetime
from typing import Any

from sqlalchemy import text

from app.db.engine import engine


def find_user_by_email(user_email: str) -> dict[str, Any] | None:
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT user_id, user_name, user_email, password_hash, created_at
                FROM users
                WHERE user_email = :user_email
                """
            ),
            {"user_email": user_email},
        ).fetchone()
    if row is None:
        return None
    return {
        "user_id": row[0],
        "user_name": row[1],
        "user_email": row[2],
        "password_hash": row[3],
        "created_at": row[4],
    }


def create_user(
    user_name: str,
    user_email: str,
    password_hash: str,
    created_at: datetime,
) -> dict[str, Any]:
    with engine.begin() as conn:
        row = conn.execute(
            text(
                """
                INSERT INTO users (user_name, user_email, password_hash, created_at)
                VALUES (:user_name, :user_email, :password_hash, :created_at)
                RETURNING user_id, user_name, user_email, created_at
                """
            ),
            {
                "user_name": user_name,
                "user_email": user_email,
                "password_hash": password_hash,
                "created_at": created_at,
            },
        ).fetchone()
    if row is None:
        raise RuntimeError("Failed to create user")
    return {
        "user_id": row[0],
        "user_name": row[1],
        "user_email": row[2],
        "created_at": row[3],
    }
