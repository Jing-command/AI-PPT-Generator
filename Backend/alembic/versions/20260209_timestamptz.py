"""Use timezone-aware timestamps.

Revision ID: 20260209_timestamptz
Revises: 
Create Date: 2026-02-09
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260209_timestamptz"
down_revision = None
branch_labels = None
depends_on = None


def _to_timestamptz(table: str, column: str) -> None:
    op.alter_column(
        table,
        column,
        type_=sa.DateTime(timezone=True),
        postgresql_using=f"{column} AT TIME ZONE 'UTC'",
    )


def _to_timestamp(table: str, column: str) -> None:
    op.alter_column(
        table,
        column,
        type_=sa.DateTime(timezone=False),
        postgresql_using=f"{column} AT TIME ZONE 'UTC'",
    )


def upgrade() -> None:
    # users
    _to_timestamptz("users", "created_at")
    _to_timestamptz("users", "updated_at")

    # templates
    _to_timestamptz("templates", "created_at")
    _to_timestamptz("templates", "updated_at")

    # presentations
    _to_timestamptz("presentations", "created_at")
    _to_timestamptz("presentations", "updated_at")

    # generation_tasks
    _to_timestamptz("generation_tasks", "created_at")
    _to_timestamptz("generation_tasks", "updated_at")
    _to_timestamptz("generation_tasks", "completed_at")

    # operation_history
    _to_timestamptz("operation_history", "created_at")
    _to_timestamptz("operation_history", "undone_at")

    # export_tasks
    _to_timestamptz("export_tasks", "created_at")
    _to_timestamptz("export_tasks", "completed_at")
    _to_timestamptz("export_tasks", "expires_at")

    # user_api_keys
    _to_timestamptz("user_api_keys", "created_at")
    _to_timestamptz("user_api_keys", "updated_at")
    _to_timestamptz("user_api_keys", "last_verified_at")


def downgrade() -> None:
    # user_api_keys
    _to_timestamp("user_api_keys", "last_verified_at")
    _to_timestamp("user_api_keys", "updated_at")
    _to_timestamp("user_api_keys", "created_at")

    # export_tasks
    _to_timestamp("export_tasks", "expires_at")
    _to_timestamp("export_tasks", "completed_at")
    _to_timestamp("export_tasks", "created_at")

    # operation_history
    _to_timestamp("operation_history", "undone_at")
    _to_timestamp("operation_history", "created_at")

    # generation_tasks
    _to_timestamp("generation_tasks", "completed_at")
    _to_timestamp("generation_tasks", "updated_at")
    _to_timestamp("generation_tasks", "created_at")

    # presentations
    _to_timestamp("presentations", "updated_at")
    _to_timestamp("presentations", "created_at")

    # templates
    _to_timestamp("templates", "updated_at")
    _to_timestamp("templates", "created_at")

    # users
    _to_timestamp("users", "updated_at")
    _to_timestamp("users", "created_at")
