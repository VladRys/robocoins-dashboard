"""add courses/groups and missing student fields

Revision ID: 8d6f8316a1c0
Revises: 56b9e2b65399
Create Date: 2026-10-05 00:00:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8d6f8316a1c0"
down_revision: Union[str, Sequence[str], None] = "56b9e2b65399"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create course/group tables and add missing student fields."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("courses"):
        op.create_table(
            "courses",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    if not inspector.has_table("groups"):
        op.create_table(
            "groups",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("course_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["course_id"], ["courses.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    existing_columns = {col["name"] for col in inspector.get_columns("students")}
    for column_name, column in {
        "group_id": sa.Column("group_id", sa.Integer(), nullable=True),
        "course": sa.Column("course", sa.String(), nullable=True),
        "avatar": sa.Column("avatar", sa.String(), nullable=True),
        "balance": sa.Column("balance", sa.Integer(), nullable=True, server_default="0"),
        "hash_access_key": sa.Column("hash_access_key", sa.String(), nullable=True),
    }.items():
        if column_name not in existing_columns:
            op.add_column("students", column)

    bind.execute(sa.text("UPDATE students SET course = :value WHERE course IS NULL"), {"value": ""})
    bind.execute(sa.text("UPDATE students SET balance = :value WHERE balance IS NULL"), {"value": 0})

    student_ids = bind.execute(
        sa.text("SELECT id FROM students WHERE hash_access_key IS NULL ORDER BY id")
    ).scalars().all()
    for student_id in student_ids:
        bind.execute(
            sa.text("UPDATE students SET hash_access_key = :value WHERE id = :student_id"),
            {"value": uuid.uuid4().hex, "student_id": student_id},
        )

    if bind.execute(sa.text("SELECT COUNT(*) FROM groups")).scalar() == 0:
        bind.execute(
            sa.text("INSERT INTO courses (id, name) VALUES (:id, :name)"),
            {"id": 1, "name": "default"},
        )
        bind.execute(
            sa.text("INSERT INTO groups (id, name, course_id) VALUES (:id, :name, :course_id)"),
            {"id": 1, "name": "default", "course_id": 1},
        )

    bind.execute(
        sa.text("UPDATE students SET group_id = :group_id WHERE group_id IS NULL"),
        {"group_id": 1},
    )

    op.create_foreign_key(
        "fk_students_group_id_groups",
        "students",
        "groups",
        ["group_id"],
        ["id"],
    )

    op.alter_column("students", "group_id", nullable=False)
    op.alter_column("students", "course", nullable=False)
    op.alter_column("students", "balance", nullable=False)
    op.alter_column("students", "hash_access_key", nullable=False)

    op.create_index(
        "uq_students_hash_access_key",
        "students",
        ["hash_access_key"],
        unique=True,
    )


def downgrade() -> None:
    """Drop course/group tables and student fields."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    student_indexes = [idx["name"] for idx in inspector.get_indexes("students") if idx.get("name")]
    if "uq_students_hash_access_key" in student_indexes:
        op.drop_index("uq_students_hash_access_key", table_name="students")

    fk_names = [fk["name"] for fk in inspector.get_foreign_keys("students") if fk.get("name")]
    if "fk_students_group_id_groups" in fk_names:
        op.drop_constraint("fk_students_group_id_groups", "students", type_="foreignkey")

    op.drop_column("students", "hash_access_key")
    op.drop_column("students", "balance")
    op.drop_column("students", "avatar")
    op.drop_column("students", "course")
    op.drop_column("students", "group_id")

    op.drop_table("groups")
    op.drop_table("courses")
