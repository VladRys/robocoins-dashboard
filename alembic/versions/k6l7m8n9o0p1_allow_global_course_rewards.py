"""Allow course rewards without a course to apply globally.

Revision ID: k6l7m8n9o0p1
Revises: j5k6l7m8n9o0
"""

from typing import Sequence, Union

from alembic import op


revision: str = "k6l7m8n9o0p1"
down_revision: Union[str, Sequence[str], None] = "j5k6l7m8n9o0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_rewards_type_course", "rewards", type_="check")
    op.create_check_constraint(
        "ck_rewards_type_course",
        "rewards",
        "(type = 'privilege' AND course_id IS NULL) OR type = 'reward'",
    )


def downgrade() -> None:
    op.execute(
        "UPDATE rewards SET type = 'privilege' "
        "WHERE type = 'reward' AND course_id IS NULL"
    )
    op.drop_constraint("ck_rewards_type_course", "rewards", type_="check")
    op.create_check_constraint(
        "ck_rewards_type_course",
        "rewards",
        "(type = 'privilege' AND course_id IS NULL) OR "
        "(type = 'reward' AND course_id IS NOT NULL)",
    )
