from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    user_id: int | None = Field(default=None, primary_key=True)
    user_name: str = Field(index=True, max_length=100, nullable=False)
    user_email: str = Field(index=True, unique=True, max_length=255, nullable=False)
    password_hash: str = Field(max_length=255, nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
