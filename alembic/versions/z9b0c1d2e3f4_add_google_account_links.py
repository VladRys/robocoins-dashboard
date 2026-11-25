"""Add Google account links and temporary OAuth state storage.

Revision ID: z9b0c1d2e3f4
Revises: y8a9b0c1d2e3
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "z9b0c1d2e3f4"
down_revision: Union[str, Sequence[str], None] = "y8a9b0c1d2e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "google_sub" not in user_columns:
        op.add_column("users", sa.Column("google_sub", sa.String(), nullable=True))
    if "google_email" not in user_columns:
        op.add_column("users", sa.Column("google_email", sa.String(), nullable=True))

    user_indexes = {index["name"] for index in inspector.get_indexes("users")}
    if "ix_users_google_sub" not in user_indexes:
        op.create_index("ix_users_google_sub", "users", ["google_sub"], unique=True)

    if not inspector.has_table("google_oauth_states"):
        op.create_table(
            "google_oauth_states",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("state_hash", sa.String(length=64), nullable=False),
            sa.Column("flow", sa.String(length=10), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("nonce", sa.String(length=64), nullable=False),
            sa.Column("code_verifier", sa.String(length=128), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("state_hash"),
        )

    state_indexes = {
        index["name"] for index in sa.inspect(bind).get_indexes("google_oauth_states")
    }
    if "ix_google_oauth_states_expires_at" not in state_indexes:
        op.create_index(
            "ix_google_oauth_states_expires_at",
            "google_oauth_states",
            ["expires_at"],
        )


def downgrade() -> None:
    op.drop_index("ix_google_oauth_states_expires_at", table_name="google_oauth_states")
    op.drop_table("google_oauth_states")
    op.drop_index("ix_users_google_sub", table_name="users")
    op.drop_column("users", "google_email")
    op.drop_column("users", "google_sub")
