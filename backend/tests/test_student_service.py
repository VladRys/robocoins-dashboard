import asyncio
import logging
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from api.routes.student import get_student_by_id as get_student_endpoint
from app.core.database import Base
from models.course import Course
from models.group import Group
from models.student import Student
from models.teacher import Teacher
from models.transaction import BalanceTransaction
from models.user import User
from repositories.student import StudentRepository
from schemas.student import StudentCreateRequest
from services.student import StudentService

logger = logging.getLogger(__name__)


def test_get_student_by_id_returns_student():
    logger.info("Requesting existing student id=%s", 123456)
    student = Student(
        id=123456,
        user_id=123456,
        name="Макс",
        group_id=1,
        course_name="Python",
        avatar="🐯",
        balance=0,
        hash_access_key="test-hash",
        access_code="ABC12345",
    )
    service = SimpleNamespace(
        get_student_by_id=AsyncMock(return_value=student)
    )

    response = asyncio.run(get_student_endpoint(123456, service))

    assert response.id == 123456
    assert response.user_id == response.id
    assert response.role == "student"
    assert response.name == "Макс"
    assert response.course_name == "Python"
    assert response.avatar == "🐯"
    assert response.balance == 0
    assert not hasattr(response, "hash_access_key")
    service.get_student_by_id.assert_awaited_once_with(123456)
    logger.info("Student id=%s returned the expected response", response.id)


def test_get_student_by_id_returns_404_when_missing():
    logger.info("Requesting missing student id=%s", 123456)
    service = SimpleNamespace(get_student_by_id=AsyncMock(return_value=None))

    with pytest.raises(HTTPException) as error:
        asyncio.run(get_student_endpoint(123456, service))

    assert error.value.status_code == 404
    assert error.value.detail == "Student not found"
    logger.info("Missing student correctly returned HTTP 404")


def test_create_student_generates_unique_hash(tmp_path: Path):
    logger.info("Starting SQLite student creation integration test")
    async def run_test():
        engine = create_async_engine(
            URL.create(
                "sqlite+aiosqlite",
                database=str(tmp_path / "students.db"),
            ),
            pool_pre_ping=True,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        try:
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)

            async with session_factory() as session:
                service = StudentService(
                    db=session,
                    repository=StudentRepository(session),
                )
                course = Course(name="Python")
                session.add(course)
                await session.flush()
                session.add(Group(id=1, name="Default", course_id=course.id))
                await session.commit()

                first_student = await service.create_student(
                    StudentCreateRequest(name="Макс", course_name="Python", group_id=1, avatar="🐯")
                )
                logger.info("Created first student id=%s", first_student.id)
                second_student = await service.create_student(
                    StudentCreateRequest(name="Иван", course_name="Python", group_id=1, avatar="🐻")
                )
                logger.info("Created second student id=%s", second_student.id)

                first_student_id = first_student.id

            async with session_factory() as verification_session:
                saved_student = await StudentRepository(
                    verification_session
                ).get_student_by_id(first_student_id)
                assert saved_student is not None
                assert saved_student.name == "Макс"
                assert saved_student.avatar == "🐯"
                assert saved_student.balance == 0
                saved_user = await verification_session.get(User, saved_student.user_id)
                assert saved_user is not None
                assert saved_user.name == saved_student.name
                assert saved_user.role == "student"
                assert first_student.hash_access_key != second_student.hash_access_key
                assert first_student.id != second_student.id
                assert first_student.id == first_student.user_id
                assert second_student.id == second_student.user_id
                logger.info("Verified persisted student data and unique identifiers")
        finally:
            await engine.dispose()

    asyncio.run(run_test())
