import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text


MIGRATION_PATH = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "s2b3c4d5e6f7_daily_tasks_use_course_ids.py"
)
SPEC = importlib.util.spec_from_file_location(
    "daily_tasks_use_course_ids",
    MIGRATION_PATH,
)
assert SPEC is not None and SPEC.loader is not None
MIGRATION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MIGRATION)


def test_daily_task_course_ids_migration_converts_and_restores_data():
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE TABLE courses "
                "(id INTEGER PRIMARY KEY, category VARCHAR NOT NULL)"
            )
        )
        connection.execute(
            text(
                "CREATE TABLE daily_task_questions "
                "(id INTEGER PRIMARY KEY, course_categories JSON NOT NULL)"
            )
        )
        connection.execute(
            text(
                "INSERT INTO courses (id, category) VALUES "
                "(2, 'python'), (4, 'python'), (5, 'math')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO daily_task_questions "
                "(id, course_categories) VALUES "
                "(1, '[\"python\"]'), (2, '[]')"
            )
        )

        with Operations.context(MigrationContext.configure(connection)):
            MIGRATION.upgrade()

        inspector = inspect(connection)
        columns = {
            column["name"]
            for column in inspector.get_columns("daily_task_questions")
        }
        assert "course_ids" in columns
        assert "course_categories" not in columns
        assert connection.execute(
            text("SELECT course_ids FROM daily_task_questions WHERE id = 1")
        ).scalar_one() == "[2, 4]"
        assert connection.execute(
            text("SELECT course_ids FROM daily_task_questions WHERE id = 2")
        ).scalar_one() == "[]"

        with Operations.context(MigrationContext.configure(connection)):
            MIGRATION.downgrade()

        assert connection.execute(
            text("SELECT course_categories FROM daily_task_questions WHERE id = 1")
        ).scalar_one() == '["python"]'
        assert connection.execute(
            text("SELECT course_categories FROM daily_task_questions WHERE id = 2")
        ).scalar_one() == "[]"
    engine.dispose()
