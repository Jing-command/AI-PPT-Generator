"""Add description column to presentations.

Revision ID: 20260209_add_description
Revises: 20260209_timestamptz
Create Date: 2026-02-09
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260209_add_description"
down_revision = "20260209_timestamptz"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "presentations",
        sa.Column("description", sa.Text(), nullable=True, comment="PPT 描述/说明")
    )


def downgrade() -> None:
    op.drop_column("presentations", "description")
