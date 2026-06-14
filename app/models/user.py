from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    user_id: str = Field(primary_key=True)
    user_name: str
    user_email: str = Field(unique=True)
    password_hash: str
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )