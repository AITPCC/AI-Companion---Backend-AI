from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from typing import Any

import psycopg

from app.core.config import get_settings


def _psycopg_url() -> str:
    return get_settings().database_url.replace("postgresql+psycopg://", "postgresql://")


@contextmanager
def get_conn() -> Generator[psycopg.Connection, None, None]:
    with psycopg.connect(_psycopg_url()) as conn:
        yield conn


def find_user_by_email(user_email: str) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT user_id, user_name, user_email, password_hash, created_at
            FROM users
            WHERE user_email = %s
            """,
            (user_email,),
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
    with get_conn() as conn:
        row = conn.execute(
            """
            INSERT INTO users (user_name, user_email, password_hash, created_at)
            VALUES (%s, %s, %s, %s)
            RETURNING user_id, user_name, user_email, created_at
            """,
            (user_name, user_email, password_hash, created_at),
        ).fetchone()
    if row is None:
        raise RuntimeError("Failed to create user")
    return {
        "user_id": row[0],
        "user_name": row[1],
        "user_email": row[2],
        "created_at": row[3],
    }
