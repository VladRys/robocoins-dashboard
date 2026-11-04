"""Synchronize daily tasks by course and date."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "t3c4d5e6f7a8"
down_revision: Union[str, Sequence[str], None] = "s2b3c4d5e6f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "course_daily_tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "course_id",
            sa.Integer(),
            sa.ForeignKey("courses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "daily_task_id",
            sa.Integer(),
            sa.ForeignKey("daily_tasks.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("task_date", sa.Date(), nullable=False),
        sa.UniqueConstraint(
            "course_id",
            "task_date",
            name="uq_course_daily_task_date",
        ),
    )
    with op.batch_alter_table("student_daily_tasks") as batch_op:
        batch_op.drop_constraint("uq_student_daily_task_date", type_="unique")
        batch_op.add_column(sa.Column("course_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_student_daily_tasks_course_id_courses",
            "courses",
            ["course_id"],
            ["id"],
            ondelete="CASCADE",
        )

    op.create_index(
        "uq_student_daily_task_course_date",
        "student_daily_tasks",
        ["student_id", "course_id", "task_date"],
        unique=True,
        postgresql_where=sa.text("course_id IS NOT NULL"),
        sqlite_where=sa.text("course_id IS NOT NULL"),
    )
    op.create_index(
        "uq_student_daily_task_unscoped_date",
        "student_daily_tasks",
        ["student_id", "task_date"],
        unique=True,
        postgresql_where=sa.text("course_id IS NULL"),
        sqlite_where=sa.text("course_id IS NULL"),
    )


def downgrade() -> None:
    connection = op.get_bind()
    duplicate_student_dates = connection.execute(
        sa.text(
            "SELECT student_id, task_date FROM student_daily_tasks "
            "GROUP BY student_id, task_date HAVING COUNT(*) > 1 LIMIT 1"
        )
    ).first()
    if duplicate_student_dates is not None:
        raise RuntimeError(
            "Cannot downgrade daily-task course assignments while a student has "
            "multiple tasks for one date."
        )

    op.drop_index(
        "uq_student_daily_task_unscoped_date",
        table_name="student_daily_tasks",
    )
    op.drop_index(
        "uq_student_daily_task_course_date",
        table_name="student_daily_tasks",
    )
    op.drop_table("course_daily_tasks")
    with op.batch_alter_table("student_daily_tasks") as batch_op:
        batch_op.drop_constraint(
            "fk_student_daily_tasks_course_id_courses",
            type_="foreignkey",
        )
        batch_op.drop_column("course_id")
        batch_op.create_unique_constraint(
            "uq_student_daily_task_date",
            ["student_id", "task_date"],
        )
