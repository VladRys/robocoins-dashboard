"""Add coin earning achievement thresholds and student assignments."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "x7f8a9b0c1d2"
down_revision: Union[str, Sequence[str], None] = "w6f7a8b9c0d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "achievements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("icon", sa.String(), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "badge",
                "trophy",
                "certificate",
                name="achievement_type",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("required_coins", sa.Integer(), nullable=True),
        sa.CheckConstraint(
            "required_coins IS NULL OR required_coins > 0",
            name="ck_achievements_required_coins_positive",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_achievements_id"),
        "achievements",
        ["id"],
        unique=False,
    )
    op.create_table(
        "student_achievements",
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("achievement_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["achievement_id"],
            ["achievements.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["students.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("student_id", "achievement_id"),
    )


def downgrade() -> None:
    op.drop_table("student_achievements")
    op.drop_index(op.f("ix_achievements_id"), table_name="achievements")
    op.drop_table("achievements")
