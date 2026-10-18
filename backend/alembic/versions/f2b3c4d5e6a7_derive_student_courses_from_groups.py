"""Derive student courses from their groups.

Revision ID: f2b3c4d5e6a7
Revises: e1a2b3c4d5f6
Create Date: 2026-10-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f2b3c4d5e6a7"
down_revision: Union[str, Sequence[str], None] = "e1a2b3c4d5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("students") as batch_op:
        batch_op.drop_constraint(
            "fk_students_course_name_courses",
            type_="foreignkey",
        )
        batch_op.drop_column("course_name")


def downgrade() -> None:
    with op.batch_alter_table("students") as batch_op:
        batch_op.add_column(sa.Column("course_name", sa.String(), nullable=True))
        batch_op.create_foreign_key(
            "fk_students_course_name_courses",
            "courses",
            ["course_name"],
            ["name"],
        )
    op.execute(
        sa.text(
            "UPDATE students SET course_name = ("
            "SELECT courses.name FROM student_groups "
            "JOIN groups ON groups.id = student_groups.group_id "
            "JOIN courses ON courses.id = groups.course_id "
            "WHERE student_groups.student_id = students.id LIMIT 1)"
        )
    )
    with op.batch_alter_table("students") as batch_op:
        batch_op.alter_column("course_name", nullable=False)
