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
    op.add_column("students", sa.Column("access_code", sa.String(), nullable=True))

    connection = op.get_bind()
    student_ids = connection.execute(sa.text("SELECT id FROM students")).scalars().all()
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    generated_codes: set[str] = set()
    for student_id in student_ids:
        code = "".join(secrets.choice(alphabet) for _ in range(8))
        while code in generated_codes:
            code = "".join(secrets.choice(alphabet) for _ in range(8))
        generated_codes.add(code)
        connection.execute(
            sa.text("UPDATE students SET access_code = :code WHERE id = :student_id"),
            {"code": code, "student_id": student_id},
        )

    with op.batch_alter_table("students") as batch_op:
        batch_op.alter_column(
            "access_code", existing_type=sa.String(), nullable=False
        )
        batch_op.create_unique_constraint("uq_students_access_code", ["access_code"])


def downgrade() -> None:
    """Remove access codes from students."""
    with op.batch_alter_table("students") as batch_op:
        batch_op.drop_constraint("uq_students_access_code", type_="unique")
        batch_op.drop_column("access_code")
