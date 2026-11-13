import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text


MIGRATION_PATH = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "y8a9b0c1d2e3_store_student_goal_reward_id.py"
)
SPEC = importlib.util.spec_from_file_location(
    "store_student_goal_reward_id",
    MIGRATION_PATH,
)
assert SPEC is not None and SPEC.loader is not None
MIGRATION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MIGRATION)


def test_student_goal_reward_id_migration_preserves_existing_goals():
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE rewards (id INTEGER PRIMARY KEY)"))
        connection.execute(
            text(
                "CREATE TABLE students ("
                "id INTEGER PRIMARY KEY, current_goal VARCHAR)"
            )
        )
        connection.execute(
            text("INSERT INTO students (id, current_goal) VALUES (1, 'Old goal')")
        )

        with Operations.context(MigrationContext.configure(connection)):
            MIGRATION.upgrade()

        student_columns = {
            column["name"] for column in inspect(connection).get_columns("students")
        }
        assert "current_goal_reward_id" in student_columns
        assert connection.execute(
            text("SELECT current_goal FROM students WHERE id = 1")
        ).scalar_one() == "Old goal"
        foreign_keys = inspect(connection).get_foreign_keys("students")
        assert any(
            foreign_key["referred_table"] == "rewards"
            and foreign_key["constrained_columns"] == ["current_goal_reward_id"]
            for foreign_key in foreign_keys
        )

        with Operations.context(MigrationContext.configure(connection)):
            MIGRATION.downgrade()
        assert "current_goal_reward_id" not in {
            column["name"] for column in inspect(connection).get_columns("students")
        }
    engine.dispose()
