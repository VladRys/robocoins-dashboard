"""Hash existing session tokens.

Revision ID: 9a4c2e1f6b80
Revises: 522532115e17
"""

from __future__ import annotations

import hashlib
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9a4c2e1f6b80"
down_revision: Union[str, Sequence[str], None] = "522532115e17"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    sessions = sa.table(
        "sessions",
        sa.column("id", sa.Integer()),
        sa.column("token_hash", sa.String()),
    )

    rows = connection.execute(
        sa.select(sessions.c.id, sessions.c.token_hash)
    ).all()
    for session_id, token in rows:
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        connection.execute(
            sessions.update()
            .where(sessions.c.id == session_id)
            .values(token_hash=token_hash)
        )


def downgrade() -> None:
    # The original tokens cannot be recovered from their hashes.
    op.execute(sa.text("DELETE FROM sessions"))
