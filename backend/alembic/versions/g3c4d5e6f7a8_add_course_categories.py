"""Add course categories.

Revision ID: g3c4d5e6f7a8
Revises: f2b3c4d5e6a7
Create Date: 2026-10-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "g3c4d5e6f7a8"
down_revision: Union[str, Sequence[str], None] = "f2b3c4d5e6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("courses") as batch_op:
        batch_op.add_column(
            sa.Column(
                "category",
                sa.String(length=11),
                nullable=False,
                server_default="other",
            )
        )
        batch_op.create_check_constraint(
            "course_category",
            "category IN ('programming', 'mathematics', 'language', 'science', 'other')",
        )


def downgrade() -> None:
    with op.batch_alter_table("courses") as batch_op:
        batch_op.drop_constraint("course_category", type_="check")
        batch_op.drop_column("category")
