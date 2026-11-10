"""Merge the balance normalization and avatar ring migration heads."""

from typing import Sequence, Union


revision: str = "w6f7a8b9c0d1"
down_revision: Union[str, Sequence[str], None] = (
    "v5e6f7a8b9c0",
    "dde9b0e8bef7",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
