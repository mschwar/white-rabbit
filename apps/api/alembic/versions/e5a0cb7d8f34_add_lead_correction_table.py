"""add lead correction table

Revision ID: e5a0cb7d8f34
Revises: 9d4e7c1f2a33
Create Date: 2026-05-10 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e5a0cb7d8f34"
down_revision: Union[str, Sequence[str], None] = "9d4e7c1f2a33"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "lead_correction",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("lead_id", sa.UUID(), nullable=False),
        sa.Column("run_id", sa.UUID(), nullable=False),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("label", sa.String(length=20), nullable=False),
        sa.Column("field_name", sa.String(length=32), nullable=False),
        sa.Column("previous_value", sa.Text(), nullable=True),
        sa.Column("corrected_value", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "label IN ('usable', 'wrong_persona', 'bad_source', 'bad_contact', 'duplicate', 'corrected_field')",
            name="ck_lead_correction_label",
        ),
        sa.CheckConstraint(
            "field_name IN ('name', 'title', 'organization', 'email', 'phone', 'source')",
            name="ck_lead_correction_field_name",
        ),
        sa.ForeignKeyConstraint(["lead_id"], ["lead.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["run_id"], ["recipe_run.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("lead_correction")
