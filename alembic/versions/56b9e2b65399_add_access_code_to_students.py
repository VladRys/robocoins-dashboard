"""add access_code to students

Revision ID: 56b9e2b65399
Revises: d6676dc933f1
Create Date: 2026-10-03 19:25:51.086777

"""
from typing import Sequence, Union
import secrets

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '56b9e2b65399'
down_revision: Union[str, Sequence[str], None] = 'd6676dc933f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add access codes to existing students."""
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_columns = {
        column["name"]: column
        for column in inspector.get_columns("students")
    }
    if "access_code" not in existing_columns:
        op.add_column(
            "students",
            sa.Column("access_code", sa.String(), nullable=True),
        )

    existing_codes = set(
        connection.execute(
            sa.text(
                "SELECT access_code FROM students "
                "WHERE access_code IS NOT NULL AND access_code != ''"
            )
        ).scalars()
    )
    student_ids = connection.execute(
        sa.text(
            "SELECT id FROM students "
            "WHERE access_code IS NULL OR access_code = ''"
        )
    ).scalars().all()
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    for student_id in student_ids:
        code = "".join(secrets.choice(alphabet) for _ in range(8))
        while code in existing_codes:
            code = "".join(secrets.choice(alphabet) for _ in range(8))
        existing_codes.add(code)
        connection.execute(
            sa.text("UPDATE students SET access_code = :code WHERE id = :student_id"),
            {"code": code, "student_id": student_id},
        )

    inspector = sa.inspect(connection)
    access_code_column = next(
        column
        for column in inspector.get_columns("students")
        if column["name"] == "access_code"
    )
    has_unique_access_code = any(
        constraint.get("column_names") == ["access_code"]
        for constraint in inspector.get_unique_constraints("students")
    ) or any(
        index.get("unique") and index.get("column_names") == ["access_code"]
        for index in inspector.get_indexes("students")
    )
    if access_code_column["nullable"] or not has_unique_access_code:
        with op.batch_alter_table("students") as batch_op:
            if access_code_column["nullable"]:
                batch_op.alter_column(
                    "access_code",
                    existing_type=sa.String(),
                    nullable=False,
                )
            if not has_unique_access_code:
                batch_op.create_unique_constraint(
                    "uq_students_access_code",
                    ["access_code"],
                )


def downgrade() -> None:
    """Remove access codes from students."""
    with op.batch_alter_table("students") as batch_op:
        batch_op.drop_constraint("uq_students_access_code", type_="unique")
        batch_op.drop_column("access_code")
