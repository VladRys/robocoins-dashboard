import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text


MIGRATION_PATH = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "x7f8a9b0c1d2_add_coin_earning_achievements.py"
)
SPEC = importlib.util.spec_from_file_location(
    "add_coin_earning_achievements",
    MIGRATION_PATH,
)
assert SPEC is not None and SPEC.loader is not None
MIGRATION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MIGRATION)


def test_coin_earning_achievement_migration_creates_and_drops_tables():
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE students (id INTEGER PRIMARY KEY)"))
        with Operations.context(MigrationContext.configure(connection)):
            MIGRATION.upgrade()

        inspector = inspect(connection)
        assert {"achievements", "student_achievements"} <= set(
            inspector.get_table_names()
        )
        assert "required_coins" in {
            column["name"] for column in inspector.get_columns("achievements")
        }

        with Operations.context(MigrationContext.configure(connection)):
            MIGRATION.downgrade()
        assert not {"achievements", "student_achievements"} & set(
            inspect(connection).get_table_names()
        )
    engine.dispose()
