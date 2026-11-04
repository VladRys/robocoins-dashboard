import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text


MIGRATION_PATH = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "p0q1r2s3t4u5_create_streaks.py"
)
SPEC = importlib.util.spec_from_file_location("create_streaks", MIGRATION_PATH)
assert SPEC is not None and SPEC.loader is not None
MIGRATION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MIGRATION)


def test_migration_creates_streaks_table_when_missing():
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE students (id INTEGER PRIMARY KEY)"))
        with Operations.context(MigrationContext.configure(connection)):
            MIGRATION.upgrade()

        columns = {column["name"] for column in inspect(connection).get_columns("streaks")}
        assert columns == {"id", "student_id", "start_date", "end_date", "days"}
    engine.dispose()


def test_migration_keeps_existing_streak_table_and_data():
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE TABLE streaks ("
                "id INTEGER PRIMARY KEY, student_id INTEGER NOT NULL, "
                "start_date DATETIME NOT NULL, end_date DATETIME, days INTEGER NOT NULL)"
            )
        )
        connection.execute(
            text("INSERT INTO streaks (id, student_id, start_date, days) VALUES (1, 8, '2026-01-01', 4)")
        )
        with Operations.context(MigrationContext.configure(connection)):
            MIGRATION.upgrade()

        saved = connection.execute(text("SELECT student_id, days FROM streaks WHERE id = 1")).one()
        assert saved == (8, 4)
    engine.dispose()
