"""add link expiry and tags

Revision ID: 4f2d0f5f8d18
Revises: fce59a06c84a
Create Date: 2026-08-05 00:00:00
"""

import sqlalchemy as sa

from alembic import op

revision = "4f2d0f5f8d18"
down_revision = "fce59a06c84a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("links", sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "links",
        sa.Column(
            "tags",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
    )


def downgrade() -> None:
    op.drop_column("links", "tags")
    op.drop_column("links", "expires_at")
