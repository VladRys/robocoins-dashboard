"""Create daily task question bank and student assignments."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "r1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "p0q1r2s3t4u5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "daily_task_questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=100), nullable=False, unique=True),
        sa.Column("question", sa.String(), nullable=False),
        sa.Column("task_type", sa.String(length=15), nullable=False),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column(
            "course_categories",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
        sa.Column("answer", sa.String(length=200), nullable=False),
        sa.Column("reward", sa.Float(), nullable=False, server_default="0.1"),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("hotspots", sa.JSON(), nullable=True),
        sa.CheckConstraint(
            "task_type IN ('multiple_choice', 'true_false', 'text', 'picture')",
            name="daily_task_type",
        ),
        sa.CheckConstraint("reward > 0", name="ck_daily_task_questions_reward_positive"),
    )
    op.create_table(
        "daily_tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "question_id",
            sa.Integer(),
            sa.ForeignKey("daily_task_questions.id", ondelete="RESTRICT"),
            nullable=False,
            unique=True,
        ),
        sa.Column("last_date", sa.Date(), nullable=True),
    )
    op.create_table(
        "student_daily_tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "student_id",
            sa.Integer(),
            sa.ForeignKey("students.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "daily_task_id",
            sa.Integer(),
            sa.ForeignKey("daily_tasks.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("task_date", sa.Date(), nullable=False),
        sa.Column("submitted_answer", sa.String(length=200), nullable=True),
        sa.Column("correct", sa.Boolean(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint(
            "student_id",
            "task_date",
            name="uq_student_daily_task_date",
        ),
    )
    op.create_index(
        "ix_student_daily_tasks_student_id",
        "student_daily_tasks",
        ["student_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_student_daily_tasks_student_id",
        table_name="student_daily_tasks",
    )
    op.drop_table("student_daily_tasks")
    op.drop_table("daily_tasks")
    op.drop_table("daily_task_questions")
