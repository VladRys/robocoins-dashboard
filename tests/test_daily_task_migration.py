import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text


MIGRATION_PATH = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "r1a2b3c4d5e6_create_daily_tasks.py"
)
SPEC = importlib.util.spec_from_file_location("create_daily_tasks", MIGRATION_PATH)
assert SPEC is not None and SPEC.loader is not None
MIGRATION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MIGRATION)


def test_daily_task_migration_creates_and_drops_task_tables():
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE students (id INTEGER PRIMARY KEY)"))
        with Operations.context(MigrationContext.configure(connection)):
            MIGRATION.upgrade()

        inspector = inspect(connection)
        assert {
            "daily_task_questions",
            "daily_tasks",
            "student_daily_tasks",
        } <= set(inspector.get_table_names())
        assert {
            "question",
            "answer",
            "task_type",
        } <= {
            column["name"]
            for column in inspector.get_columns("daily_task_questions")
        }

        with Operations.context(MigrationContext.configure(connection)):
            MIGRATION.downgrade()
        assert not {
            "daily_task_questions",
            "daily_tasks",
            "student_daily_tasks",
        } & set(inspect(connection).get_table_names())
    engine.dispose()
