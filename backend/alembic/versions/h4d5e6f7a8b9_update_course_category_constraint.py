"""Update allowed course category values.

Revision ID: h4d5e6f7a8b9
Revises: g3c4d5e6f7a8
Create Date: 2026-10-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "h4d5e6f7a8b9"
down_revision: Union[str, Sequence[str], None] = "g3c4d5e6f7a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ALLOWED_CATEGORIES = "'embedded', 'game dev', 'web', 'primary', 'python', 'no category'"


def upgrade() -> None:
    with op.batch_alter_table("courses") as batch_op:
        batch_op.drop_constraint("course_category", type_="check")
        batch_op.alter_column("category", server_default="no category")

    op.execute(
        sa.text(
            "UPDATE courses SET category = 'no category' "
            f"WHERE category NOT IN ({ALLOWED_CATEGORIES})"
        )
    )

    with op.batch_alter_table("courses") as batch_op:
        batch_op.create_check_constraint(
            "course_category",
            f"category IN ({ALLOWED_CATEGORIES})",
        )


def downgrade() -> None:
    old_categories = "'programming', 'mathematics', 'language', 'science', 'other'"
    with op.batch_alter_table("courses") as batch_op:
        batch_op.drop_constraint("course_category", type_="check")

    op.execute(
        sa.text(
            "UPDATE courses SET category = 'other' "
            f"WHERE category NOT IN ({old_categories})"
        )
    )

    with op.batch_alter_table("courses") as batch_op:
        batch_op.alter_column("category", server_default="other")
        batch_op.create_check_constraint(
            "course_category",
            f"category IN ({old_categories})",
        )
