"""Add users, teacher profiles, and group teacher assignments.

Revision ID: 6c2a1e9f4b70
Revises: 9a4c2e1f6b80
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6c2a1e9f4b70"
down_revision: Union[str, Sequence[str], None] = "9a4c2e1f6b80"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.CheckConstraint(
            "role IN ('student', 'teacher')",
            name="ck_users_role",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "teachers",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_teachers_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id"),
    )

    op.add_column(
        "students",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )
    bind = op.get_bind()
    bind.execute(
        sa.text(
            "INSERT INTO users (id, name, role) "
            "SELECT id, name, 'student' FROM students"
        )
    )
    bind.execute(sa.text("UPDATE students SET user_id = id"))
    if bind.dialect.name == "postgresql":
        bind.execute(
            sa.text(
                "SELECT setval("
                "pg_get_serial_sequence('users', 'id'), "
                "COALESCE((SELECT MAX(id) FROM users), 1), "
                "EXISTS (SELECT 1 FROM users)"
                ")"
            )
        )

    with op.batch_alter_table("students") as batch_op:
        batch_op.alter_column("user_id", nullable=False)
        batch_op.create_foreign_key(
            "fk_students_user_id_users",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )
        batch_op.create_unique_constraint("uq_students_user_id", ["user_id"])

    with op.batch_alter_table("groups") as batch_op:
        batch_op.add_column(sa.Column("teacher_1_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("teacher_2_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_groups_teacher_1_id_teachers",
            "teachers",
            ["teacher_1_id"],
            ["user_id"],
            ondelete="SET NULL",
        )
        batch_op.create_foreign_key(
            "fk_groups_teacher_2_id_teachers",
            "teachers",
            ["teacher_2_id"],
            ["user_id"],
            ondelete="SET NULL",
        )
        batch_op.create_check_constraint(
            "ck_groups_distinct_teachers",
            "teacher_1_id IS NULL OR teacher_1_id != teacher_2_id",
        )


def downgrade() -> None:
    with op.batch_alter_table("groups") as batch_op:
        batch_op.drop_constraint(
            "ck_groups_distinct_teachers",
            type_="check",
        )
        batch_op.drop_constraint(
            "fk_groups_teacher_2_id_teachers",
            type_="foreignkey",
        )
        batch_op.drop_constraint(
            "fk_groups_teacher_1_id_teachers",
            type_="foreignkey",
        )
        batch_op.drop_column("teacher_2_id")
        batch_op.drop_column("teacher_1_id")

    with op.batch_alter_table("students") as batch_op:
        batch_op.drop_constraint("uq_students_user_id", type_="unique")
        batch_op.drop_constraint(
            "fk_students_user_id_users",
            type_="foreignkey",
        )
        batch_op.drop_column("user_id")

    op.drop_table("teachers")
    op.drop_table("users")
