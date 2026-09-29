import asyncio
import logging
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from api.routes.student import get_student_by_id as get_student_endpoint
from core.database import Base
from models.student import Student
from repositories.student import StudentRepository
from schemas.student import StudentCreateRequest
from services.student import StudentService

logger = logging.getLogger(__name__)


def test_get_student_by_id_returns_student():
    logger.info("Requesting existing student id=%s", 123456)
    student = Student(
        id=123456,
        name="Макс",
        group="Junior",
        avatar="🐯",
        balance=0,
        hash_access_key="test-hash",
    )
    service = SimpleNamespace(
        get_student_by_id=AsyncMock(return_value=student)
    )

    response = asyncio.run(get_student_endpoint(123456, service))

    assert response.id == 123456
    assert response.name == "Макс"
    assert response.group == "Junior"
    assert response.avatar == "🐯"
    assert response.balance == 0
    assert response.hash_access_key == "test-hash"
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


def test_create_student_generates_unique_hash():
    logger.info("Starting PostgreSQL student creation integration test")
    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("Set TEST_DATABASE_URL to run the PostgreSQL integration test")
    if not database_url.startswith(("postgresql://", "postgresql+psycopg://", "postgresql+asyncpg://")):
        pytest.fail("TEST_DATABASE_URL must point to a PostgreSQL database")
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://", "postgresql+psycopg://", 1
        )

    async def run_test():
        engine = create_async_engine(database_url, pool_pre_ping=True)
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        created_hashes = []

        try:
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)

            async with session_factory() as session:
                service = StudentService(
                    db=session,
                    repository=StudentRepository(session),
                )

                first_student = await service.create_student(
                    StudentCreateRequest(name="Макс", group="Junior", avatar="🐯")
                )
                created_hashes.append(first_student.hash_access_key)
                logger.info("Created first student id=%s", first_student.id)
                second_student = await service.create_student(
                    StudentCreateRequest(name="Иван", group="Junior", avatar="🐻")
                )
                created_hashes.append(second_student.hash_access_key)
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
                assert first_student.hash_access_key != second_student.hash_access_key
                assert first_student.id != second_student.id
                logger.info("Verified persisted student data and unique identifiers")
        finally:
            if created_hashes:
                logger.info("Cleaning up integration-test student records")
                async with session_factory() as cleanup_session:
                    await cleanup_session.execute(
                        delete(Student).where(
                            Student.hash_access_key.in_(created_hashes)
                        )
                    )
                    await cleanup_session.commit()
            await engine.dispose()

    asyncio.run(run_test())
