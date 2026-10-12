"""add sessions and auth

Revision ID: 522532115e17
Revises: 4e8af671c20b
Create Date: 2026-10-09 17:41:51.652411

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "522532115e17"
down_revision: Union[str, Sequence[str], None] = "4e8af671c20b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create session storage and align student/course constraints."""
    with op.batch_alter_table("courses") as batch_op:
        batch_op.create_unique_constraint("uq_courses_name", ["name"])

    with op.batch_alter_table("students") as batch_op:
        batch_op.drop_index("uq_students_hash_access_key")
        batch_op.create_unique_constraint(
            "uq_students_hash_access_key",
            ["hash_access_key"],
        )
        batch_op.create_foreign_key(
            "fk_students_course_name_courses",
            "courses",
            ["course_name"],
            ["name"],
        )

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("sessions"):
        op.create_table(
            "sessions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("token_hash", sa.String(), nullable=False),
            sa.Column("student_id", sa.Integer(), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(
                ["student_id"],
                ["students.id"],
                name="fk_sessions_student_id_students",
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("sessions")}
    required_columns = {"id", "token_hash", "student_id", "expires_at"}
    missing_columns = required_columns - columns
    if missing_columns:
        raise RuntimeError(
            "Existing sessions table is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    has_unique_token_hash = any(
        index.get("unique")
        and index.get("column_names") == ["token_hash"]
        for index in inspector.get_indexes("sessions")
    ) or any(
        constraint.get("column_names") == ["token_hash"]
        for constraint in inspector.get_unique_constraints("sessions")
    )
    if not has_unique_token_hash:
        op.create_index(
            "ix_sessions_token_hash",
            "sessions",
            ["token_hash"],
            unique=True,
        )


def downgrade() -> None:
    """Remove session storage and restore the previous constraints."""
    op.drop_table("sessions")

    with op.batch_alter_table("students") as batch_op:
        batch_op.drop_constraint(
            "fk_students_course_name_courses",
            type_="foreignkey",
        )
        batch_op.drop_constraint(
            "uq_students_hash_access_key",
            type_="unique",
        )
        batch_op.create_index(
            "uq_students_hash_access_key",
            ["hash_access_key"],
            unique=True,
        )

    with op.batch_alter_table("courses") as batch_op:
        batch_op.drop_constraint("uq_courses_name", type_="unique")
