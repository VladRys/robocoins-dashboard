import asyncio
import importlib.util
import sys
from pathlib import Path

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from fastapi import Request
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from unittest.mock import AsyncMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from api.routes.course import get_courses
from api.routes.group import (
    create_group,
    get_group_by_id,
    get_group_by_name,
    get_groups_by_course_id,
)
from api.routes.auth import get_current_student
from api.routes.student import create_student
from api.routes.student import get_student_by_id
from api.routes.teacher import register_teacher
from api.routes.users import get_user_by_id, get_users
from app.core.database import Base
from models.course import Course
from models.student import Student
from repositories.group import GroupRepository
from repositories.course import CourseRepository
from repositories.student import StudentRepository
from repositories.users import UserRepository
from schemas.group import GroupCreateRequest
from schemas.student import StudentCreateRequest
from schemas.teacher import TeacherRegistrationRequest
from services.group import GroupService
from services.course import CourseService
from services.student import StudentService
from services.users import UserService


def test_auth_me_returns_user_profile_fields():
    async def run_test():
        student = Student(
            id=123456,
            user_id=123456,
            name="Student One",
            group_id=1,
            course_name="Python",
            avatar="🤖",
            balance=10,
            hash_access_key="hash",
            access_code="CODE1234",
        )

        class ActiveSession:
            student_id = student.id

            def is_expired(self) -> bool:
                return False

        session_service = AsyncMock()
        session_service.get_session_by_token.return_value = ActiveSession()
        student_service = AsyncMock()
        student_service.get_student_by_id.return_value = student
        request = Request(
            {
                "type": "http",
                "asgi": {"version": "3.0"},
                "http_version": "1.1",
                "method": "GET",
                "scheme": "http",
                "path": "/auth/me",
                "raw_path": b"/auth/me",
                "query_string": b"",
                "headers": [(b"cookie", b"session_token=test-token")],
                "server": ("test", 80),
                "client": ("test", 123),
                "root_path": "",
            }
        )

        profile = await get_current_student(
            request,
            student_service=student_service,
            session_service=session_service,
        )

        assert profile.user_id == profile.id == student.user_id
        assert profile.role == "student"
        assert profile.model_dump(mode="json")["user_id"] == profile.id
        student_service.get_student_by_id.assert_awaited_once_with(student.id)

    asyncio.run(run_test())


def test_student_and_teacher_registration_and_group_assignments(tmp_path: Path):
    async def run_test():
        engine = create_async_engine(
            URL.create(
                "sqlite+aiosqlite",
                database=str(tmp_path / "users.db"),
            ),
            pool_pre_ping=True,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        try:
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)

            async with session_factory() as session:
                user_service = UserService(UserRepository(session))
                teacher_one = await register_teacher(
                    TeacherRegistrationRequest(name="Teacher One"),
                    user_service,
                )
                teacher_two = await register_teacher(
                    TeacherRegistrationRequest(name="Teacher Two"),
                    user_service,
                )
                assert teacher_one.role == "teacher"
                assert teacher_two.role == "teacher"

                course = Course(name="Python")
                session.add(course)
                await session.flush()
                group_service = GroupService(
                    session,
                    GroupRepository(session),
                )
                group_response = await create_group(
                    GroupCreateRequest(
                        name="Group A",
                        course_id=course.id,
                        teacher_ids=[teacher_one.id, teacher_two.id],
                    ),
                    service=group_service,
                )
                assert group_response.teacher_ids == [
                    teacher_one.id,
                    teacher_two.id,
                ]
                group_by_id = await get_group_by_id(
                    group_response.id,
                    service=group_service,
                )
                group_by_name = await get_group_by_name(
                    "Group A",
                    service=group_service,
                )
                groups_by_course = await get_groups_by_course_id(
                    course.id,
                    service=group_service,
                )
                course_list = await get_courses(
                    service=CourseService(CourseRepository(session))
                )
                for group_profile in (
                    group_by_id,
                    group_by_name,
                    groups_by_course[0],
                    course_list[0].groups[0],
                ):
                    assert group_profile.teacher_ids == [
                        teacher_one.id,
                        teacher_two.id,
                    ]

                student_service = StudentService(
                    session,
                    StudentRepository(session),
                )
                student_response = await create_student(
                    StudentCreateRequest(
                        name="Student One",
                        avatar="🤖",
                        course_name=course.name,
                        group_id=group_response.id,
                    ),
                    service=student_service,
                )
                assert student_response.role == "student"
                assert student_response.id == student_response.user_id
                student_profile = await get_student_by_id(
                    student_response.id,
                    service=student_service,
                )
                assert student_profile.user_id == student_profile.id
                assert student_profile.role == "student"
                student = await StudentRepository(session).get_student_by_id(
                    student_response.id
                )
                assert student is not None
                student_user = await user_service.get_user_by_id(student.id)
                assert student_user is not None
                assert student_user.role == "student"
                assert student_user.name == student.name
                assert student.user_id == student.id
                assert (await get_user_by_id(student.id, user_service)).role == "student"
                assert {user.role for user in await get_users(user_service)} == {
                    "student",
                    "teacher",
                }

                assigned_group = await group_service.assign_group_teachers(
                    group_response.id,
                    [teacher_two.id],
                )
                assert assigned_group is not None
                assert assigned_group.teacher_1_id == teacher_two.id
                assert assigned_group.teacher_2_id is None
                assert len(await user_service.get_users()) == 3

                with pytest.raises(ValueError, match="at most two"):
                    await group_service.assign_group_teachers(
                        group_response.id,
                        [teacher_one.id, teacher_two.id, 999],
                    )
        finally:
            await engine.dispose()
    asyncio.run(run_test())


def test_user_migration_creates_accounts_for_existing_students():
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "6c2a1e9f4b70_add_users_teachers_and_group_assignments.py"
    )
    spec = importlib.util.spec_from_file_location(
        "add_user_roles_migration",
        migration_path,
    )
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    engine = create_engine("sqlite://")
    try:
        with engine.begin() as connection:
            connection.execute(
                text("CREATE TABLE students (id INTEGER PRIMARY KEY, name VARCHAR NOT NULL)")
            )
            connection.execute(text("CREATE TABLE groups (id INTEGER PRIMARY KEY)"))
            connection.execute(
                text(
                    "INSERT INTO students (id, name) VALUES "
                    "(123456, 'Existing Student')"
                )
            )

            with Operations.context(MigrationContext.configure(connection)):
                migration.upgrade()

            migrated_user = connection.execute(
                text("SELECT id, name, role FROM users")
            ).one()
            migrated_student = connection.execute(
                text("SELECT user_id FROM students WHERE id = 123456")
            ).scalar_one()
            assert migrated_user == (123456, "Existing Student", "student")
            assert migrated_student == migrated_user.id
    finally:
        engine.dispose()


def test_student_id_migration_preserves_related_records_and_handles_collisions():
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "8f3c2a7d1e60_use_user_ids_for_student_profiles.py"
    )
    spec = importlib.util.spec_from_file_location(
        "use_user_ids_for_student_profiles",
        migration_path,
    )
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    engine = create_engine("sqlite://")
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "CREATE TABLE users ("
                    "id INTEGER PRIMARY KEY, "
                    "name VARCHAR NOT NULL, "
                    "role VARCHAR(20) NOT NULL)"
                )
            )
            connection.execute(
                text(
                    "CREATE TABLE students ("
                    "id INTEGER PRIMARY KEY, "
                    "user_id INTEGER NOT NULL UNIQUE, "
                    "name VARCHAR NOT NULL, "
                    "CONSTRAINT fk_students_user_id_users "
                    "FOREIGN KEY(user_id) REFERENCES users(id))"
                )
            )
            connection.execute(
                text(
                    "CREATE TABLE sessions ("
                    "id INTEGER PRIMARY KEY, "
                    "student_id INTEGER NOT NULL, "
                    "CONSTRAINT fk_sessions_student_id_students "
                    "FOREIGN KEY(student_id) REFERENCES students(id))"
                )
            )
            connection.execute(
                text(
                    "CREATE TABLE balance_transactions ("
                    "id INTEGER PRIMARY KEY, "
                    "student_id INTEGER NOT NULL, "
                    "FOREIGN KEY(student_id) REFERENCES students(id))"
                )
            )
            connection.execute(
                text(
                    "INSERT INTO users (id, name, role) VALUES "
                    "(2, 'User 2', 'student'), "
                    "(100, 'User 100', 'student'), "
                    "(300, 'User 300', 'student')"
                )
            )
            connection.execute(
                text(
                    "INSERT INTO students (id, user_id, name) VALUES "
                    "(2, 100, 'Student 100'), "
                    "(100, 300, 'Student 300'), "
                    "(300, 2, 'Student 2')"
                )
            )
            connection.execute(
                text(
                    "INSERT INTO sessions (id, student_id) VALUES "
                    "(1, 2), (2, 100), (3, 300)"
                )
            )
            connection.execute(
                text(
                    "INSERT INTO balance_transactions (id, student_id) VALUES "
                    "(1, 2), (2, 100), (3, 300)"
                )
            )

            with Operations.context(MigrationContext.configure(connection)):
                migration.upgrade()

            students = connection.execute(
                text("SELECT id, user_id FROM students ORDER BY id")
            ).all()
            assert students == [(2, 2), (100, 100), (300, 300)]
            assert connection.execute(
                text("SELECT student_id FROM sessions ORDER BY id")
            ).scalars().all() == [100, 300, 2]
            assert connection.execute(
                text("SELECT student_id FROM balance_transactions ORDER BY id")
            ).scalars().all() == [100, 300, 2]
            assert connection.execute(text("PRAGMA foreign_key_check")).all() == []
    finally:
        engine.dispose()
