"""Store the selected reward ID with each student's goal."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "y8a9b0c1d2e3"
down_revision: Union[str, Sequence[str], None] = "x7f8a9b0c1d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("students") as batch_op:
        batch_op.add_column(
            sa.Column("current_goal_reward_id", sa.Integer(), nullable=True),
        )
        batch_op.create_foreign_key(
            "fk_students_current_goal_reward_id_rewards",
            "rewards",
            ["current_goal_reward_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("students") as batch_op:
        batch_op.drop_constraint(
            "fk_students_current_goal_reward_id_rewards",
            type_="foreignkey",
        )
        batch_op.drop_column("current_goal_reward_id")
