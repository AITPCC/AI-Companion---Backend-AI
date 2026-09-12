"""Fixed-window budgets. Each operation owns a short database transaction."""

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256

from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session
from starlette.concurrency import run_in_threadpool

from app.db import database
from app.db.engine import engine
from app.models.quota import Quota


@dataclass(frozen=True)
class Budget:
    kind: str
    identity: str
    endpoint: str
    limit: int
    window_seconds: int


@dataclass(frozen=True)
class Reservation:
    budget: Budget
    window_start: datetime


def identity_key(*parts: str) -> str:
    """Hash the complete tuple; never truncate identities or store raw emails."""
    return sha256(json.dumps(parts, ensure_ascii=True).encode()).hexdigest()


def get_window_start(window_seconds: int) -> datetime:
    now = int(datetime.now(timezone.utc).timestamp())
    return datetime.fromtimestamp(now // window_seconds * window_seconds, timezone.utc)


def reserve(budget: Budget) -> Reservation:
    window = get_window_start(budget.window_seconds)
    try:
        with Session(engine) as session:
            allowed = database.reserve_quota(
                session,
                budget.kind,
                budget.identity,
                budget.endpoint,
                window,
                budget.limit,
            )
    except SQLAlchemyError as exc:
        raise HTTPException(503, "Quota service temporarily unavailable") from exc
    if not allowed:
        retry_after = max(
            1,
            int(
                window.timestamp()
                + budget.window_seconds
                - datetime.now(timezone.utc).timestamp()
            )
            + 1,
        )
        raise HTTPException(
            429, "Too many requests", headers={"Retry-After": str(retry_after)}
        )
    return Reservation(budget, window)


def refund(reservation: Reservation) -> None:
    """Refund this window only, even if authentication crosses a window boundary."""
    budget = reservation.budget
    try:
        with Session(engine) as session:
            session.execute(
                update(Quota)
                .where(
                    Quota.actor_kind == budget.kind,
                    Quota.actor_id == budget.identity,
                    Quota.endpoint == budget.endpoint,
                    Quota.window_start == reservation.window_start,
                    Quota.request_count > 0,
                )
                .values(request_count=Quota.request_count - 1)
            )
            session.commit()
    except SQLAlchemyError as exc:
        raise HTTPException(503, "Quota service temporarily unavailable") from exc


async def reserve_async(budget: Budget) -> Reservation:
    # The session is created inside the worker, never shared across threads.
    return await run_in_threadpool(reserve, budget)
