"""Use UTC instants for quota windows and index retention scans.

Revision ID: c13a00000001
Revises: b02c738c8086
"""

import sqlalchemy as sa

from alembic import op

revision = "c13a00000001"
down_revision = "b02c738c8086"
branch_labels = None
depends_on = None


def upgrade():
    # Existing rows were written with a UTC database session. Verify before rollout.
    op.alter_column(
        "quotas",
        "window_start",
        type_=sa.DateTime(timezone=True),
        postgresql_using="window_start AT TIME ZONE 'UTC'",
    )
    op.create_index("ix_quotas_window_start", "quotas", ["window_start"])


def downgrade():
    op.drop_index("ix_quotas_window_start", table_name="quotas")
    op.alter_column(
        "quotas",
        "window_start",
        type_=sa.DateTime(timezone=False),
        postgresql_using="window_start AT TIME ZONE 'UTC'",
    )
