import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text


MIGRATION_PATH = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "t3c4d5e6f7a8_sync_daily_tasks_by_course.py"
)
SPEC = importlib.util.spec_from_file_location(
    "sync_daily_tasks_by_course",
    MIGRATION_PATH,
)
assert SPEC is not None and SPEC.loader is not None
MIGRATION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MIGRATION)


def test_daily_task_course_assignment_migration_creates_and_drops_schema():
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE courses (id INTEGER PRIMARY KEY)"))
        connection.execute(text("CREATE TABLE students (id INTEGER PRIMARY KEY)"))
        connection.execute(text("CREATE TABLE daily_tasks (id INTEGER PRIMARY KEY)"))
        connection.execute(
            text(
                "CREATE TABLE student_daily_tasks ("
                "id INTEGER PRIMARY KEY, "
                "student_id INTEGER NOT NULL REFERENCES students(id), "
                "daily_task_id INTEGER NOT NULL REFERENCES daily_tasks(id), "
                "task_date DATE NOT NULL, "
                "CONSTRAINT uq_student_daily_task_date "
                "UNIQUE (student_id, task_date)"
                ")"
            )
        )

        with Operations.context(MigrationContext.configure(connection)):
            MIGRATION.upgrade()

        inspector = inspect(connection)
        assert "course_daily_tasks" in inspector.get_table_names()
        assert "course_id" in {
            column["name"]
            for column in inspector.get_columns("student_daily_tasks")
        }
        assert {
            "uq_student_daily_task_course_date",
            "uq_student_daily_task_unscoped_date",
        } <= {
            index["name"] for index in inspector.get_indexes("student_daily_tasks")
        }

        with Operations.context(MigrationContext.configure(connection)):
            MIGRATION.downgrade()

        inspector = inspect(connection)
        assert "course_daily_tasks" not in inspector.get_table_names()
        assert "course_id" not in {
            column["name"]
            for column in inspector.get_columns("student_daily_tasks")
        }
        assert "uq_student_daily_task_date" in {
            constraint["name"]
            for constraint in inspector.get_unique_constraints("student_daily_tasks")
        }
    engine.dispose()
