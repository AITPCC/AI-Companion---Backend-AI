from datetime import datetime

from sqlalchemy import DateTime, UniqueConstraint
from sqlmodel import SQLModel, Field


class Quota(SQLModel, table=True):
    __tablename__ = "quotas"
    __table_args__ = (
        UniqueConstraint(
            "actor_kind", "actor_id", "endpoint", "window_start", name="uq_quota_key"
        ),
    )

    quota_id: int | None = Field(default=None, primary_key=True)
    actor_kind: str = Field(max_length=10, nullable=False)
    actor_id: str = Field(max_length=255, nullable=False)
    endpoint: str = Field(max_length=50, nullable=False)
    window_start: datetime = Field(sa_type=DateTime(timezone=True), nullable=False)
    request_count: int = Field(default=0, nullable=False)
