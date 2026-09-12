from sqlmodel import create_engine

from app.core.config import get_settings

# Bound connection acquisition, lock contention, and database execution.
engine = create_engine(
    get_settings().database_url,
    pool_timeout=5,
    pool_pre_ping=True,
    connect_args={
        "connect_timeout": 5,
        "options": "-c statement_timeout=5000 -c lock_timeout=2000",
    },
)
