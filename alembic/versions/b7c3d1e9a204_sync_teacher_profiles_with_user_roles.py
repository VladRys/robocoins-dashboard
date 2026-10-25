"""Create teacher profiles for users with the teacher role.

Revision ID: b7c3d1e9a204
Revises: 8f3c2a7d1e60
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7c3d1e9a204"
down_revision: Union[str, Sequence[str], None] = "8f3c2a7d1e60"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text(
            "INSERT INTO teachers (user_id) "
            "SELECT id FROM users WHERE role = 'teacher' "
            "ON CONFLICT (user_id) DO NOTHING"
        )
    )

    if bind.dialect.name == "postgresql":
        op.execute(
            """
            CREATE FUNCTION sync_teacher_profile() RETURNS TRIGGER
            LANGUAGE plpgsql AS $$
            BEGIN
                IF NEW.role = 'teacher' THEN
                    INSERT INTO teachers (user_id)
                    VALUES (NEW.id)
                    ON CONFLICT (user_id) DO NOTHING;
                ELSE
                    DELETE FROM teachers WHERE user_id = NEW.id;
                END IF;
                RETURN NEW;
            END;
            $$;
            """
        )
        op.execute(
            """
            CREATE TRIGGER users_teacher_profile_after_insert
            AFTER INSERT ON users
            FOR EACH ROW EXECUTE FUNCTION sync_teacher_profile();
            """
        )
        op.execute(
            """
            CREATE TRIGGER users_teacher_profile_after_role_update
            AFTER UPDATE OF role ON users
            FOR EACH ROW EXECUTE FUNCTION sync_teacher_profile();
            """
        )
    elif bind.dialect.name == "sqlite":
        op.execute(
            """
            CREATE TRIGGER users_teacher_profile_after_insert
            AFTER INSERT ON users
            WHEN NEW.role = 'teacher'
            BEGIN
                INSERT OR IGNORE INTO teachers (user_id) VALUES (NEW.id);
            END;
            """
        )
        op.execute(
            """
            CREATE TRIGGER users_teacher_profile_after_role_update
            AFTER UPDATE OF role ON users
            BEGIN
                INSERT OR IGNORE INTO teachers (user_id)
                SELECT NEW.id WHERE NEW.role = 'teacher';
                DELETE FROM teachers
                WHERE user_id = NEW.id AND NEW.role != 'teacher';
            END;
            """
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP TRIGGER IF EXISTS users_teacher_profile_after_insert ON users")
        op.execute(
            "DROP TRIGGER IF EXISTS users_teacher_profile_after_role_update ON users"
        )
        op.execute("DROP FUNCTION IF EXISTS sync_teacher_profile()")
    elif bind.dialect.name == "sqlite":
        op.execute("DROP TRIGGER IF EXISTS users_teacher_profile_after_insert")
        op.execute("DROP TRIGGER IF EXISTS users_teacher_profile_after_role_update")
