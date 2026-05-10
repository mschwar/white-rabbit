"""allow synthetic correction identifiers

Revision ID: 6c9d2f10a9b1
Revises: e5a0cb7d8f34
Create Date: 2026-05-10 20:10:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "6c9d2f10a9b1"
down_revision = "e5a0cb7d8f34"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("lead_correction_lead_id_fkey", "lead_correction", type_="foreignkey")
    op.drop_constraint("lead_correction_run_id_fkey", "lead_correction", type_="foreignkey")
    op.alter_column(
        "lead_correction",
        "lead_id",
        existing_type=postgresql.UUID(as_uuid=True),
        type_=sa.Text(),
        postgresql_using="lead_id::text",
        nullable=False,
    )
    op.alter_column(
        "lead_correction",
        "run_id",
        existing_type=postgresql.UUID(as_uuid=True),
        type_=sa.Text(),
        postgresql_using="run_id::text",
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "lead_correction",
        "run_id",
        existing_type=sa.Text(),
        type_=postgresql.UUID(as_uuid=True),
        postgresql_using="run_id::uuid",
        nullable=False,
    )
    op.alter_column(
        "lead_correction",
        "lead_id",
        existing_type=sa.Text(),
        type_=postgresql.UUID(as_uuid=True),
        postgresql_using="lead_id::uuid",
        nullable=False,
    )
    op.create_foreign_key(
        "lead_correction_run_id_fkey",
        "lead_correction",
        "recipe_run",
        ["run_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "lead_correction_lead_id_fkey",
        "lead_correction",
        "lead",
        ["lead_id"],
        ["id"],
        ondelete="CASCADE",
    )
