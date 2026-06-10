from sqlmodel import SQLModel

from app.models.user import User

# Import table models here so Alembic autogenerate picks them up.

__all__ = ["SQLModel", "User"]
