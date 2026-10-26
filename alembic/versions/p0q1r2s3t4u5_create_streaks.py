"""Create student streak records."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "p0q1r2s3t4u5"
down_revision: Union[str, Sequence[str], None] = "n9o0p1q2r3s4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "streaks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=True),
        sa.Column("days", sa.Integer(), server_default="0", nullable=False),
    )


def downgrade() -> None:
    op.drop_table("streaks")
