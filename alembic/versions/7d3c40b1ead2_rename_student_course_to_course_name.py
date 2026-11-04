"""rename student course to course_name

Revision ID: 7d3c40b1ead2
Revises: 8d6f8316a1c0
Create Date: 2026-10-05 00:00:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7d3c40b1ead2"
down_revision: Union[str, Sequence[str], None] = "8d6f8316a1c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename students.course to students.course_name and move legacy group values."""
    bind = op.get_bind()

    def current_columns() -> set[str]:
        return {column["name"] for column in sa.inspect(bind).get_columns("students")}

    existing_columns = current_columns()

    if "course_name" not in existing_columns and "course" in existing_columns:
        op.execute("ALTER TABLE students RENAME COLUMN course TO course_name")
        existing_columns = current_columns()

    if "group" in existing_columns:
        if "course_name" not in existing_columns:
            op.execute("ALTER TABLE students ADD COLUMN course_name VARCHAR")
            existing_columns = current_columns()

        bind.execute(
            sa.text(
                """
                UPDATE students
                SET course_name = "group"
                WHERE course_name IS NULL OR course_name = ''
                """
            )
        )

        bind.execute(sa.text('ALTER TABLE students DROP COLUMN "group"'))


def downgrade() -> None:
    """Restore students.course and drop migrated legacy values."""
    bind = op.get_bind()

    def current_columns() -> set[str]:
        return {column["name"] for column in sa.inspect(bind).get_columns("students")}

    existing_columns = current_columns()

    if "course" not in existing_columns and "course_name" in existing_columns:
        op.execute("ALTER TABLE students RENAME COLUMN course_name TO course")
