"""Use course IDs to target daily tasks.

Revision ID: s2b3c4d5e6f7
Revises: r1a2b3c4d5e6
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "s2b3c4d5e6f7"
down_revision: Union[str, Sequence[str], None] = "r1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _course_categories_by_id(connection: sa.Connection) -> dict[int, str]:
    courses = sa.Table(
        "courses",
        sa.MetaData(),
        sa.Column("id", sa.Integer()),
        sa.Column("category", sa.String()),
    )
    return {
        course_id: category
        for course_id, category in connection.execute(
            sa.select(courses.c.id, courses.c.category)
        )
    }


def upgrade() -> None:
    connection = op.get_bind()
    categories_by_course_id = _course_categories_by_id(connection)
    course_ids_by_category: dict[str, list[int]] = {}
    for course_id, category in categories_by_course_id.items():
        course_ids_by_category.setdefault(category, []).append(course_id)

    questions = sa.Table(
        "daily_task_questions",
        sa.MetaData(),
        sa.Column("id", sa.Integer()),
        sa.Column("course_ids", sa.JSON()),
    )
    with op.batch_alter_table("daily_task_questions") as batch_op:
        batch_op.alter_column(
            "course_categories",
            new_column_name="course_ids",
            existing_type=sa.JSON(),
            existing_nullable=False,
        )

    rows = connection.execute(
        sa.select(questions.c.id, questions.c.course_ids)
    ).all()
    for question_id, categories in rows:
        course_ids = sorted(
            {
                course_id
                for category in categories
                for course_id in course_ids_by_category.get(category, [])
            }
        )
        connection.execute(
            sa.update(questions)
            .where(questions.c.id == question_id)
            .values(course_ids=course_ids)
        )


def downgrade() -> None:
    connection = op.get_bind()
    categories_by_course_id = _course_categories_by_id(connection)
    questions = sa.Table(
        "daily_task_questions",
        sa.MetaData(),
        sa.Column("id", sa.Integer()),
        sa.Column("course_categories", sa.JSON()),
    )
    with op.batch_alter_table("daily_task_questions") as batch_op:
        batch_op.alter_column(
            "course_ids",
            new_column_name="course_categories",
            existing_type=sa.JSON(),
            existing_nullable=False,
        )

    rows = connection.execute(
        sa.select(questions.c.id, questions.c.course_categories)
    ).all()
    for question_id, course_ids in rows:
        categories = sorted(
            {
                categories_by_course_id[course_id]
                for course_id in course_ids
                if course_id in categories_by_course_id
            }
        )
        connection.execute(
            sa.update(questions)
            .where(questions.c.id == question_id)
            .values(course_categories=categories)
        )
