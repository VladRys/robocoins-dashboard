"""Add access codes to users and make sessions user-based.

Revision ID: c4f8a91d2e70
Revises: b7c3d1e9a204
"""

from __future__ import annotations

import secrets
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4f8a91d2e70"
down_revision: Union[str, Sequence[str], None] = "b7c3d1e9a204"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _generate_access_code(existing_codes: set[str]) -> str:
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    while True:
        code = "".join(secrets.choice(alphabet) for _ in range(8))
        if code not in existing_codes:
            existing_codes.add(code)
            return code


def upgrade() -> None:
    bind = op.get_bind()
    orphaned_session = bind.execute(
        sa.text(
            """
            SELECT sessions.id
            FROM sessions
            LEFT JOIN students ON students.id = sessions.student_id
            WHERE students.user_id IS NULL
            LIMIT 1
            """
        )
    ).scalar_one_or_none()
    if orphaned_session is not None:
        raise RuntimeError(
            "Cannot migrate session without a matching user for session "
            f"{orphaned_session}"
        )

    op.add_column(
        "users",
        sa.Column("access_code", sa.String(), nullable=True),
    )

    bind.execute(
        sa.text(
            """
            UPDATE users
            SET access_code = (
                SELECT students.access_code
                FROM students
                WHERE students.user_id = users.id
            )
            WHERE role = 'student'
            """
        )
    )
    existing_codes = set(
        bind.execute(
            sa.text(
                "SELECT access_code FROM users WHERE access_code IS NOT NULL"
            )
        ).scalars()
    )
    users_without_codes = bind.execute(
        sa.text("SELECT id FROM users WHERE access_code IS NULL ORDER BY id")
    ).scalars().all()
    for user_id in users_without_codes:
        bind.execute(
            sa.text("UPDATE users SET access_code = :code WHERE id = :user_id"),
            {"code": _generate_access_code(existing_codes), "user_id": user_id},
        )

    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "access_code",
            existing_type=sa.String(),
            nullable=False,
        )
        batch_op.create_unique_constraint(
            "uq_users_access_code",
            ["access_code"],
        )

    if bind.dialect.name == "postgresql":
        op.execute(
            """
            CREATE FUNCTION generate_user_access_code() RETURNS TRIGGER
            LANGUAGE plpgsql AS $$
            DECLARE
                alphabet CONSTANT TEXT :=
                    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
                candidate TEXT;
                attempts INTEGER;
                char_position INTEGER;
            BEGIN
                IF NEW.access_code IS NOT NULL AND NEW.access_code != '' THEN
                    RETURN NEW;
                END IF;

                FOR attempts IN 1..100 LOOP
                    candidate := '';
                    FOR char_position IN 1..8 LOOP
                        candidate := candidate || substr(
                            alphabet,
                            floor(random() * length(alphabet))::INTEGER + 1,
                            1
                        );
                    END LOOP;
                    EXIT WHEN NOT EXISTS (
                        SELECT 1 FROM users WHERE access_code = candidate
                    );
                    candidate := NULL;
                END LOOP;

                IF candidate IS NULL THEN
                    RAISE EXCEPTION 'Could not generate a unique user access code';
                END IF;
                NEW.access_code := candidate;
                RETURN NEW;
            END;
            $$;
            """
        )
        op.execute(
            """
            CREATE TRIGGER users_generate_access_code_before_insert
            BEFORE INSERT ON users
            FOR EACH ROW EXECUTE FUNCTION generate_user_access_code();
            """
        )

    op.add_column(
        "sessions",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )
    bind.execute(
        sa.text(
            """
            UPDATE sessions
            SET user_id = (
                SELECT students.user_id
                FROM students
                WHERE students.id = sessions.student_id
            )
            """
        )
    )
    with op.batch_alter_table("sessions") as batch_op:
        batch_op.alter_column(
            "user_id",
            existing_type=sa.Integer(),
            nullable=False,
        )
        batch_op.alter_column(
            "student_id",
            existing_type=sa.Integer(),
            nullable=True,
        )
        batch_op.create_foreign_key(
            "fk_sessions_user_id_users",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])


def downgrade() -> None:
    bind = op.get_bind()
    teacher_sessions = bind.execute(
        sa.text("SELECT id FROM sessions WHERE student_id IS NULL LIMIT 1")
    ).scalar_one_or_none()
    if teacher_sessions is not None:
        raise RuntimeError(
            "Cannot downgrade while teacher sessions exist; "
            f"session {teacher_sessions} has no student_id"
        )

    if bind.dialect.name == "postgresql":
        op.execute(
            "DROP TRIGGER IF EXISTS users_generate_access_code_before_insert ON users"
        )
        op.execute("DROP FUNCTION IF EXISTS generate_user_access_code()")

    op.drop_index("ix_sessions_user_id", table_name="sessions")
    with op.batch_alter_table("sessions") as batch_op:
        batch_op.drop_constraint(
            "fk_sessions_user_id_users",
            type_="foreignkey",
        )
        batch_op.drop_column("user_id")
        batch_op.alter_column(
            "student_id",
            existing_type=sa.Integer(),
            nullable=False,
        )

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("uq_users_access_code", type_="unique")
        batch_op.drop_column("access_code")
