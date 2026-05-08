"""add sandbox_state table

Revision ID: 8ddb2b783647
Revises: 129492e59179
Create Date: 2026-05-08 13:22:23.311183

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ddb2b783647'
down_revision: Union[str, Sequence[str], None] = '129492e59179'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create sandbox_state table and seed the singleton row."""
    op.create_table(
        'sandbox_state',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('total_queries', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_rows', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_queries', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('max_rows', sa.Integer(), nullable=False, server_default='1000'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('reset_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    # Seed the singleton row that get_sandbox_state expects
    op.bulk_insert(
        sa.table(
            'sandbox_state',
            sa.column('id', sa.Integer()),
            sa.column('total_queries', sa.Integer()),
            sa.column('total_rows', sa.Integer()),
            sa.column('max_queries', sa.Integer()),
            sa.column('max_rows', sa.Integer()),
        ),
        [
            {'id': 1, 'total_queries': 0, 'total_rows': 0, 'max_queries': 10, 'max_rows': 1000},
        ],
    )


def downgrade() -> None:
    """Drop sandbox_state table."""
    op.drop_table('sandbox_state')
