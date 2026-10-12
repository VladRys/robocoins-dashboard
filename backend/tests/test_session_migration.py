import hashlib
import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, text


MIGRATION_PATH = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "9a4c2e1f6b80_hash_existing_session_tokens.py"
)
SPEC = importlib.util.spec_from_file_location("hash_session_tokens", MIGRATION_PATH)
assert SPEC is not None and SPEC.loader is not None
MIGRATION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MIGRATION)


def test_migration_hashes_existing_tokens_and_downgrade_clears_sessions():
    engine = create_engine("sqlite://")
    legacy_tokens = ["legacy-token-one", "legacy-token-two"]

    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE TABLE sessions "
                "(id INTEGER PRIMARY KEY, token_hash VARCHAR NOT NULL)"
            )
        )
        connection.execute(
            text(
                "INSERT INTO sessions (id, token_hash) "
                "VALUES (:id, :token)"
            ),
            [
                {"id": index, "token": token}
                for index, token in enumerate(legacy_tokens, start=1)
            ],
        )

        with Operations.context(MigrationContext.configure(connection)):
            MIGRATION.upgrade()

        migrated_tokens = connection.execute(
            text("SELECT token_hash FROM sessions ORDER BY id")
        ).scalars().all()
        assert migrated_tokens == [
            hashlib.sha256(token.encode("utf-8")).hexdigest()
            for token in legacy_tokens
        ]

        with Operations.context(MigrationContext.configure(connection)):
            MIGRATION.downgrade()

        remaining_sessions = connection.execute(
            text("SELECT COUNT(*) FROM sessions")
        ).scalar_one()
        assert remaining_sessions == 0

    engine.dispose()
