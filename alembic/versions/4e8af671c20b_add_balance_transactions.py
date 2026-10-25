"""add balance transactions

Revision ID: 4e8af671c20b
Revises: 7d3c40b1ead2
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4e8af671c20b"
down_revision: Union[str, Sequence[str], None] = "7d3c40b1ead2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "balance_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("operation", sa.String(length=20), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "amount > 0",
            name="ck_balance_transactions_amount_positive",
        ),
        sa.CheckConstraint(
            "operation IN ('deposit', 'deduct')",
            name="ck_balance_transactions_operation",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["students.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_balance_transactions_student_id",
        "balance_transactions",
        ["student_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_balance_transactions_student_id",
        table_name="balance_transactions",
    )
    op.drop_table("balance_transactions")
