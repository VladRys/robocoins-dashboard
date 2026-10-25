"""Add reward types and optional course association.

Revision ID: j5k6l7m8n9o0
Revises: d9e5f3a2b710
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "j5k6l7m8n9o0"
down_revision: Union[str, Sequence[str], None] = "d9e5f3a2b710"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "rewards",
        sa.Column(
            "type",
            sa.String(),
            nullable=False,
            server_default="privilege",
        ),
    )
    op.add_column(
        "rewards",
        sa.Column("course_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_rewards_course_id_courses",
        "rewards",
        "courses",
        ["course_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_check_constraint(
        "ck_rewards_type_course",
        "rewards",
        "(type = 'privilege' AND course_id IS NULL) OR "
        "(type = 'reward' AND course_id IS NOT NULL)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_rewards_type_course", "rewards", type_="check")
    op.drop_constraint("fk_rewards_course_id_courses", "rewards", type_="foreignkey")
    op.drop_column("rewards", "course_id")
    op.drop_column("rewards", "type")
