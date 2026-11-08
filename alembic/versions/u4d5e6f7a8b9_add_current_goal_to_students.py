"""Add current goal to students."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "u4d5e6f7a8b9"
down_revision: Union[str, Sequence[str], None] = "t3c4d5e6f7a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "students",
        sa.Column("current_goal", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("students", "current_goal")
