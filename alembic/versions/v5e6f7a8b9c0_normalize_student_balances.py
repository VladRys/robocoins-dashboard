"""Normalize stored student balances to one decimal place."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "v5e6f7a8b9c0"
down_revision: Union[str, Sequence[str], None] = "u4d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL's two-argument round operates on numeric, so cast the float.
    op.execute(
        sa.text(
            "UPDATE students "
            "SET balance = ROUND(balance::numeric, 1)::double precision "
            "WHERE balance <> ROUND(balance::numeric, 1)::double precision"
        )
    )


def downgrade() -> None:
    # The previous precision cannot be recovered after normalization.
    pass
