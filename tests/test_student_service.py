import asyncio
import logging
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.routes.student import (
    change_goal as change_goal_endpoint,
    get_balance_leaderboard_rank,
    get_student_by_id as get_student_endpoint,
)
from app.core.database import Base
from app.core.enums import HttpErrorMessage
from app.models.course import Course
from app.models.group import Group
from app.models.user import User
from app.repositories.student import StudentRepository
from app.schemas.student import StudentCreateRequest, StudentGoalChangeRequest
from app.services.student import StudentService
from tests.conftest import student_with_groups

logger = logging.getLogger(__name__)


def test_change_goal_endpoint_saves_selected_reward_name():
    student = SimpleNamespace(id=123456)
    reward = SimpleNamespace(
        id=987,
        name="Новая цель",
        price=100,
        description=None,
        type="reward",
        course_category=None,
    )
    student_service = SimpleNamespace(
        get_student_by_id=AsyncMock(return_value=student),
        change_student_goal=AsyncMock(return_value=student),
    )
    reward_service = SimpleNamespace(
        get_reward_by_id=AsyncMock(return_value=reward),
    )

    response = asyncio.run(
        change_goal_endpoint(
            123456,
            StudentGoalChangeRequest(new_goal_reward_id=987),
            student_service,
            reward_service,
            SimpleNamespace(),
        )
    )

    assert response.new_goal.id == 987
    student_service.change_student_goal.assert_awaited_once_with(
        123456,
        "Новая цель",
    )


def test_get_student_by_id_returns_student():
    logger.info("Requesting existing student id=%s", 123456)
    student = student_with_groups(
        student_id=123456,
        name="Макс",
        avatar="🐯",
    )
    student.current_goal = "Новая цель"
    service = SimpleNamespace(
        get_student_by_id=AsyncMock(return_value=student)
    )

    response = asyncio.run(get_student_endpoint(123456, service))

    assert response.id == 123456
    assert response.user_id == response.id
    assert response.role == "student"
    assert response.name == "Макс"
    assert response.course_names == ["Python"]
    assert response.group_ids == [1]
    assert response.avatar == "🐯"
    assert response.avatar_ring is None
    assert response.balance == 0.0
    assert response.current_goal == "Новая цель"
    assert not hasattr(response, "hash_access_key")
    service.get_student_by_id.assert_awaited_once_with(123456)
    logger.info("Student id=%s returned the expected response", response.id)


def test_get_student_by_id_returns_404_when_missing():
    logger.info("Requesting missing student id=%s", 123456)
    service = SimpleNamespace(get_student_by_id=AsyncMock(return_value=None))

    with pytest.raises(HTTPException) as error:
        asyncio.run(get_student_endpoint(123456, service))

    assert error.value.status_code == 404
    assert error.value.detail == HttpErrorMessage.STUDENT_NOT_FOUND
    logger.info("Missing student correctly returned HTTP 404")


@pytest.mark.parametrize(
    ("avatar", "avatar_ring"),
    [("🐯", "gold"), (None, None)],
)
def test_get_balance_leaderboard_rank_returns_student_details(avatar, avatar_ring):
    student = SimpleNamespace(
        id=123456,
        name="Макс",
        avatar=avatar,
        avatar_ring=avatar_ring,
        balance=42.5,
    )
    service = SimpleNamespace(
        get_balance_leaderboard_rank=AsyncMock(return_value=(3, student))
    )

    response = asyncio.run(
        get_balance_leaderboard_rank(123456, service, SimpleNamespace())
    )

    assert response.student_id == 123456
    assert response.student_avatar == avatar
    assert response.avatar_ring == avatar_ring
    assert response.name == "Макс"
    assert response.rank == 3
    assert response.balance == 42.5
    service.get_balance_leaderboard_rank.assert_awaited_once_with(123456)


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
                service = StudentService(repository=StudentRepository(session))
                course = Course(name="Python")
                session.add(course)
                await session.flush()
                group = Group(id=1, name="Default", course_id=course.id)
                session.add(group)
                await session.commit()

                first_student = await service.create_student(
                    StudentCreateRequest(
                        name="Макс",
                        avatar="🐯",
                        group_ids=[1],
                    )
                )
                logger.info("Created first student id=%s", first_student.id)
                second_student = await service.create_student(
                    StudentCreateRequest(
                        name="Иван",
                        avatar="🐻",
                        group_ids=[1],
                    )
                )
                logger.info("Created second student id=%s", second_student.id)

                first_student_id = first_student.id
                updated_student = await service.change_student_goal(
                    first_student_id,
                    "Python course",
                )
                assert updated_student is not None
                assert updated_student.current_goal == "Python course"

            async with session_factory() as verification_session:
                saved_student = await StudentRepository(
                    verification_session
                ).get_student_by_id(first_student_id)
                assert saved_student is not None
                assert saved_student.name == "Макс"
                assert saved_student.avatar == "🐯"
                assert saved_student.balance == 0.0
                assert saved_student.current_goal == "Python course"
                assert [group.id for group in saved_student.groups] == [1]
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
