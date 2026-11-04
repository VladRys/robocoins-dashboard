"""Add optional description to rewards.

Revision ID: d9e5f3a2b710
Revises: c8d4e2f1a609
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d9e5f3a2b710"
down_revision: Union[str, Sequence[str], None] = "c8d4e2f1a609"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "rewards",
        sa.Column("description", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("rewards", "description")
