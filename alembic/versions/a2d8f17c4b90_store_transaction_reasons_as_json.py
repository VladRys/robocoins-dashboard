"""Store transaction reasons as a JSON array.

Revision ID: a2d8f17c4b90
Revises: h4d5e6f7a8b9
"""

from __future__ import annotations

import json
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a2d8f17c4b90"
down_revision: Union[str, Sequence[str], None] = "h4d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _as_reason_list(value: object) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, list):
        values = value
    elif isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            parsed = None
        values = parsed if isinstance(parsed, list) else value.split(", ")
    else:
        values = [str(value)]
    return [str(item).strip() for item in values if str(item).strip()]


def _read_reasons(bind) -> list[tuple[int, object]]:
    return list(
        bind.execute(
            sa.text("SELECT id, reason FROM balance_transactions WHERE reason IS NOT NULL")
        )
    )


def _write_reasons(bind, values: list[tuple[int, str]]) -> None:
    for transaction_id, reason in values:
        bind.execute(
            sa.text("UPDATE balance_transactions SET reason = :reason WHERE id = :id"),
            {"id": transaction_id, "reason": reason},
        )


def upgrade() -> None:
    bind = op.get_bind()
    normalized = [
        (transaction_id, json.dumps(reasons, ensure_ascii=False))
        for transaction_id, value in _read_reasons(bind)
        if (reasons := _as_reason_list(value)) is not None
    ]
    _write_reasons(bind, normalized)

    if bind.dialect.name == "postgresql":
        op.alter_column(
            "balance_transactions",
            "reason",
            existing_type=sa.String(),
            type_=sa.JSON(),
            postgresql_using="reason::json",
            existing_nullable=True,
        )
    else:
        with op.batch_alter_table("balance_transactions") as batch_op:
            batch_op.alter_column(
                "reason",
                existing_type=sa.String(),
                type_=sa.JSON(),
                existing_nullable=True,
            )


def downgrade() -> None:
    bind = op.get_bind()
    flattened = [
        (transaction_id, ", ".join(reasons))
        for transaction_id, value in _read_reasons(bind)
        if (reasons := _as_reason_list(value)) is not None
    ]

    if bind.dialect.name == "postgresql":
        op.alter_column(
            "balance_transactions",
            "reason",
            existing_type=sa.JSON(),
            type_=sa.String(),
            postgresql_using="reason::text",
            existing_nullable=True,
        )
    else:
        with op.batch_alter_table("balance_transactions") as batch_op:
            batch_op.alter_column(
                "reason",
                existing_type=sa.JSON(),
                type_=sa.String(),
                existing_nullable=True,
            )

    _write_reasons(bind, flattened)
