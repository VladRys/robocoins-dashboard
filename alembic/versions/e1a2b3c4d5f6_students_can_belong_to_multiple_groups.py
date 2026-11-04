"""Allow students to belong to multiple groups.

Revision ID: e1a2b3c4d5f6
Revises: c4f8a91d2e70
Create Date: 2026-10-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e1a2b3c4d5f6"
down_revision: Union[str, Sequence[str], None] = "c4f8a91d2e70"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "student_groups",
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("student_id", "group_id"),
    )
    op.execute(
        sa.text(
            "INSERT INTO student_groups (student_id, group_id) "
            "SELECT id, group_id FROM students WHERE group_id IS NOT NULL"
        )
    )
    with op.batch_alter_table("students") as batch_op:
        batch_op.drop_column("group_id")


def downgrade() -> None:
    with op.batch_alter_table("students") as batch_op:
        batch_op.add_column(sa.Column("group_id", sa.Integer(), nullable=True))
    op.execute(
        sa.text(
            "UPDATE students SET group_id = ("
            "SELECT group_id FROM student_groups "
            "WHERE student_groups.student_id = students.id LIMIT 1)"
        )
    )
    with op.batch_alter_table("students") as batch_op:
        batch_op.alter_column("group_id", nullable=False)
        batch_op.create_foreign_key(
            "fk_students_group_id_groups", "groups", ["group_id"], ["id"]
        )
    op.drop_table("student_groups")
