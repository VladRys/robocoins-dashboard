"""Associate rewards with course categories instead of course IDs.

Revision ID: l7m8n9o0p1q2
Revises: k6l7m8n9o0p1
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "l7m8n9o0p1q2"
down_revision: Union[str, Sequence[str], None] = "k6l7m8n9o0p1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("rewards", sa.Column("course_category", sa.String(), nullable=True))
    op.execute(
        "UPDATE rewards SET course_category = ("
        "SELECT courses.category FROM courses "
        "WHERE courses.id = rewards.course_id"
        ") WHERE course_id IS NOT NULL"
    )

    with op.batch_alter_table("rewards") as batch_op:
        batch_op.drop_constraint("ck_rewards_type_course", type_="check")
        batch_op.drop_constraint("fk_rewards_course_id_courses", type_="foreignkey")
        batch_op.drop_column("course_id")
        batch_op.create_check_constraint(
            "ck_rewards_type_course_category",
            "(type = 'privilege' AND course_category IS NULL) OR type = 'reward'",
        )
        batch_op.create_check_constraint(
            "reward_type",
            "type IN ('privilege', 'reward')",
        )
        batch_op.create_check_constraint(
            "reward_course_category",
            "course_category IN ('embedded', 'game dev', 'web', 'primary', 'python', 'no category') "
            "OR course_category IS NULL",
        )


def downgrade() -> None:
    op.add_column("rewards", sa.Column("course_id", sa.Integer(), nullable=True))
    op.execute(
        "UPDATE rewards SET course_id = ("
        "SELECT courses.id FROM courses "
        "WHERE courses.category = rewards.course_category LIMIT 1"
        ") WHERE course_category IS NOT NULL"
    )

    with op.batch_alter_table("rewards") as batch_op:
        batch_op.drop_constraint("ck_rewards_type_course_category", type_="check")
        batch_op.drop_constraint("reward_type", type_="check")
        batch_op.drop_constraint("reward_course_category", type_="check")
        batch_op.drop_column("course_category")
        batch_op.create_foreign_key(
            "fk_rewards_course_id_courses",
            "courses",
            ["course_id"],
            ["id"],
            ondelete="CASCADE",
        )
        batch_op.create_check_constraint(
            "ck_rewards_type_course",
            "(type = 'privilege' AND course_id IS NULL) OR type = 'reward'",
        )
