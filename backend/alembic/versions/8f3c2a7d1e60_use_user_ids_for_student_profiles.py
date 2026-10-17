"""Use user IDs as student profile IDs.

Revision ID: 8f3c2a7d1e60
Revises: 6c2a1e9f4b70
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8f3c2a7d1e60"
down_revision: Union[str, Sequence[str], None] = "6c2a1e9f4b70"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_FK_NAMING_CONVENTION = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}


def _drop_student_foreign_key(table_name: str) -> None:
    inspector = sa.inspect(op.get_bind())
    foreign_keys = [
        foreign_key
        for foreign_key in inspector.get_foreign_keys(table_name)
        if foreign_key["referred_table"] == "students"
        and foreign_key["constrained_columns"] == ["student_id"]
    ]
    if not foreign_keys:
        return

    with op.batch_alter_table(
        table_name,
        naming_convention=_FK_NAMING_CONVENTION,
    ) as batch_op:
        for foreign_key in foreign_keys:
            name = foreign_key["name"] or (
                f"fk_{table_name}_student_id_students"
            )
            batch_op.drop_constraint(name, type_="foreignkey")


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    student_ids = [
        (row.id, row.user_id)
        for row in bind.execute(
            sa.text("SELECT id, user_id FROM students ORDER BY id")
        )
    ]
    changed_ids = [
        (student_id, user_id)
        for student_id, user_id in student_ids
        if student_id != user_id
    ]

    if changed_ids:
        for table_name in ("sessions", "balance_transactions"):
            if inspector.has_table(table_name):
                _drop_student_foreign_key(table_name)

        current_max = max(
            max(student_id for student_id, _ in student_ids),
            max(user_id for _, user_id in student_ids),
        )
        temporary_ids = {
            old_id: current_max + index
            for index, (old_id, _) in enumerate(changed_ids, start=1)
        }
        students = sa.table(
            "students",
            sa.column("id", sa.Integer()),
            sa.column("user_id", sa.Integer()),
        )
        for old_id, temporary_id in temporary_ids.items():
            bind.execute(
                students.update()
                .where(students.c.id == old_id)
                .values(id=temporary_id)
            )
        for old_id, user_id in changed_ids:
            bind.execute(
                students.update()
                .where(students.c.id == temporary_ids[old_id])
                .values(id=user_id)
            )

        for table_name in ("sessions", "balance_transactions"):
            if not inspector.has_table(table_name):
                continue
            child = sa.table(
                table_name,
                sa.column("student_id", sa.Integer()),
            )
            for old_id, _ in changed_ids:
                bind.execute(
                    child.update()
                    .where(child.c.student_id == old_id)
                    .values(student_id=temporary_ids[old_id])
                )
            for old_id, user_id in changed_ids:
                bind.execute(
                    child.update()
                    .where(child.c.student_id == temporary_ids[old_id])
                    .values(student_id=user_id)
                )

        for table_name in ("sessions", "balance_transactions"):
            if not inspector.has_table(table_name):
                continue
            with op.batch_alter_table(
                table_name,
                naming_convention=_FK_NAMING_CONVENTION,
            ) as batch_op:
                batch_op.create_foreign_key(
                    f"fk_{table_name}_student_id_students",
                    "students",
                    ["student_id"],
                    ["id"],
                    ondelete="CASCADE",
                )

    with op.batch_alter_table("students") as batch_op:
        batch_op.create_foreign_key(
            "fk_students_id_users",
            "users",
            ["id"],
            ["id"],
            ondelete="CASCADE",
        )
        batch_op.create_check_constraint(
            "ck_students_id_matches_user_id",
            "id = user_id",
        )

    if bind.dialect.name == "postgresql":
        bind.execute(
            sa.text(
                "SELECT setval("
                "pg_get_serial_sequence('students', 'id'), "
                "COALESCE((SELECT MAX(id) FROM students), 1), "
                "EXISTS (SELECT 1 FROM students)"
                ")"
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("students") as batch_op:
        batch_op.drop_constraint(
            "ck_students_id_matches_user_id",
            type_="check",
        )
        batch_op.drop_constraint(
            "fk_students_id_users",
            type_="foreignkey",
        )
