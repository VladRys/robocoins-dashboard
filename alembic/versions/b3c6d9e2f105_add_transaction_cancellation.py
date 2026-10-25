"""Add cancellation metadata to balance transactions.

Revision ID: b3c6d9e2f105
Revises: a2d8f17c4b90
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b3c6d9e2f105"
down_revision: Union[str, Sequence[str], None] = "a2d8f17c4b90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "balance_transactions",
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "balance_transactions",
        sa.Column(
            "cancelled_by_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("balance_transactions", "cancelled_by_user_id")
    op.drop_column("balance_transactions", "cancelled_at")
