"""add feedback label check constraint

Revision ID: 9d4e7c1f2a33
Revises: 8ddb2b783647
Create Date: 2026-05-09 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '9d4e7c1f2a33'
down_revision: Union[str, Sequence[str], None] = '8ddb2b783647'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


VALID_LABELS_CHECK = "label IN ('usable', 'wrong_persona', 'bad_source', 'bad_contact', 'duplicate')"


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        f"ALTER TABLE lead_feedback ADD CONSTRAINT ck_lead_feedback_label CHECK ({VALID_LABELS_CHECK}) NOT VALID"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE lead_feedback DROP CONSTRAINT IF EXISTS ck_lead_feedback_label")
