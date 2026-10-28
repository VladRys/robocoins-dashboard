import asyncio
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock
from urllib.parse import unquote
from xml.etree import ElementTree

import pytest
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.routes.daily_task import (
    answer_daily_task,
    answer_daily_task_test_task,
    get_daily_task,
    get_daily_task_test_tasks,
)
from app.core.database import Base
from app.core.enums import AuthorizationAction, ProductMode, TaskType, UserRole
from app.models.course import Course  # noqa: F401
from app.models.daily_task import DailyTask, DailyTaskQuestion
from app.models.group import Group  # noqa: F401
from app.models.student import Student
from app.models.streak import Streak  # noqa: F401
from app.models.teacher import Teacher  # noqa: F401
from app.models.transaction import BalanceTransaction
from app.models.user import User
from app.schemas.daily_task import DailyTaskAnswer
from app.services.daily_task import (
    DailyTaskAlreadyCompletedError,
    DailyTaskService,
)


def test_daily_task_routes_use_authorization_service():
    async def run():
        user = SimpleNamespace(id=12, role=UserRole.TEACHER.value)
        authorization = SimpleNamespace(is_allowed=AsyncMock(return_value=False))
        service = SimpleNamespace(
            get_or_create=AsyncMock(),
            answer=AsyncMock(),
        )

        with pytest.raises(HTTPException) as get_error:
            await get_daily_task(
                34,
                user=user,
                service=service,
                authorization=authorization,
            )
        assert get_error.value.status_code == 403
        authorization.is_allowed.assert_awaited_once_with(
            AuthorizationAction.ACCESS_DAILY_TASK,
            user,
            34,
        )
        service.get_or_create.assert_not_awaited()

        authorization.is_allowed.reset_mock()
        with pytest.raises(HTTPException) as answer_error:
            await answer_daily_task(
                34,
                DailyTaskAnswer(answer="answer"),
                user=user,
                service=service,
                authorization=authorization,
            )
        assert answer_error.value.status_code == 403
        authorization.is_allowed.assert_awaited_once_with(
            AuthorizationAction.ACCESS_DAILY_TASK,
            user,
            34,
        )
        service.answer.assert_not_awaited()

    asyncio.run(run())


def test_seeded_picture_task_uses_data_url_images():
    from scripts.seed_daily_tasks import TASKS

    picture_task = TASKS["picture_led"]
    options = picture_task["options"]
    assert len(options) == 4
    assert len(picture_task["answer"]) <= 200
    assert picture_task["answer"] == "1"
    assert 0 <= int(picture_task["answer"]) < len(options)
    for image_url in options:
        prefix, encoded_image = image_url.split(",", maxsplit=1)
        assert prefix == "data:image/svg+xml"
        ElementTree.fromstring(unquote(encoded_image))


def test_daily_task_test_routes_require_student_authorization(monkeypatch):
    async def run():
        from app.api.routes import daily_task as daily_task_routes

        monkeypatch.setattr(
            daily_task_routes.Config,
            "PRODUCT_MODE",
            ProductMode.DEV,
        )
        user = SimpleNamespace(id=12, role=UserRole.TEACHER.value)
        authorization = SimpleNamespace(is_allowed=AsyncMock(return_value=False))
        service = SimpleNamespace(
            get_test_tasks=AsyncMock(),
            answer_test_task=AsyncMock(),
        )

        with pytest.raises(HTTPException) as list_error:
            await get_daily_task_test_tasks(
                34,
                user=user,
                service=service,
                authorization=authorization,
            )
        assert list_error.value.status_code == 403
        service.get_test_tasks.assert_not_awaited()

        with pytest.raises(HTTPException) as answer_error:
            await answer_daily_task_test_task(
                34,
                1,
                DailyTaskAnswer(answer="answer"),
                user=user,
                service=service,
                authorization=authorization,
            )
        assert answer_error.value.status_code == 403
        service.answer_test_task.assert_not_awaited()

        monkeypatch.setattr(
            daily_task_routes.Config,
            "PRODUCT_MODE",
            ProductMode.PROD,
        )
        with pytest.raises(HTTPException) as mode_error:
            await get_daily_task_test_tasks(
                34,
                user=user,
                service=service,
                authorization=authorization,
            )
        assert mode_error.value.status_code == 404

    asyncio.run(run())


def test_daily_task_answer_locks_only_assignment_row():
    async def run():
        db = SimpleNamespace(scalar=AsyncMock(return_value=None))
        await DailyTaskService(db)._get_assignment(1, date.today(), lock=True)

        statement = db.scalar.await_args.args[0]
        sql = str(statement.compile(dialect=postgresql.dialect()))
        assert "FOR UPDATE OF student_daily_tasks" in sql
        assert "FOR UPDATE OF daily_tasks" not in sql
        assert "FOR UPDATE OF daily_task_questions" not in sql

    asyncio.run(run())


def test_daily_task_hides_answer_and_awards_correct_submission_once():
    async def run():
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        sessions = async_sessionmaker(engine, expire_on_commit=False)
        async with sessions() as session:
            user = User(
                id=1,
                name="Student",
                role=UserRole.STUDENT.value,
                access_code="ABC12345",
            )
            student = Student(
                id=1,
                user_id=1,
                name="Student",
                balance=0,
                hash_access_key="test-key",
                access_code="ABC12345",
            )
            question = DailyTaskQuestion(
                slug="test-question",
                question="Which component emits light?",
                task_type=TaskType.MULTIPLE_CHOICE,
                options=["Resistor", "LED"],
                answer="LED",
                reward=0.1,
            )
            task = DailyTask(question=question)
            session.add_all([user, student, task])
            await session.commit()

            service = DailyTaskService(session)
            response = await service.get_or_create(1)
            assert response.question == question.question
            assert "answer" not in response.model_dump()
            assert response.date == date.today()
            assert await service.get_or_create(1) == response

            result = await service.answer(1, " led ")
            assert result.correct is True
            assert result.reward == 0.1
            assert result.balance == 0.1
            assert "answer" not in result.model_dump()

            with pytest.raises(DailyTaskAlreadyCompletedError):
                await service.answer(1, "LED")

            assert await session.scalar(
                select(func.count()).select_from(BalanceTransaction)
            ) == 1
            assert await session.scalar(
                select(Student.balance).where(Student.id == 1)
            ) == 0.1

        await engine.dispose()

    asyncio.run(run())


def test_daily_task_test_flow_returns_ordered_questions_without_rewards():
    async def run():
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        sessions = async_sessionmaker(engine, expire_on_commit=False)
        async with sessions() as session:
            first_question = DailyTaskQuestion(
                slug="test-first",
                question="Which component emits light?",
                task_type=TaskType.MULTIPLE_CHOICE,
                options=["Resistor", "LED"],
                answer="LED",
            )
            second_question = DailyTaskQuestion(
                slug="test-second",
                question="Start a Python conditional",
                task_type=TaskType.TEXT,
                answer="if",
            )
            picture_question = DailyTaskQuestion(
                slug="test-picture",
                question="Choose the LED",
                task_type=TaskType.PICTURE,
                options=[
                    "data:image/svg+xml;base64,cmVzaXN0b3I=",
                    "data:image/svg+xml;base64,bGVk",
                    "data:image/svg+xml;base64,YnV0dG9u",
                    "data:image/svg+xml;base64,d2lyZQ==",
                ],
                answer="1",
            )
            first_task = DailyTask(question=first_question)
            second_task = DailyTask(question=second_question)
            picture_task = DailyTask(question=picture_question)
            session.add_all([first_task, second_task, picture_task])
            await session.commit()

            service = DailyTaskService(session)
            tasks = await service.get_test_tasks()
            assert [task.id for task in tasks] == [
                first_task.id,
                second_task.id,
                picture_task.id,
            ]
            assert [task.question for task in tasks] == [
                first_question.question,
                second_question.question,
                picture_question.question,
            ]
            assert tasks[2].options == picture_question.options
            assert len(tasks[2].options) == 4
            assert all(
                option.startswith("data:image/") for option in tasks[2].options
            )
            assert tasks[2].hotspots is None
            assert all("answer" not in task.model_dump() for task in tasks)

            assert (await service.answer_test_task(first_task.id, " led ")).correct
            assert not (await service.answer_test_task(second_task.id, "else")).correct
            assert (
                await service.answer_test_task(
                    picture_task.id,
                    "1",
                )
            ).correct
            assert await session.scalar(
                select(func.count()).select_from(BalanceTransaction)
            ) == 0

        await engine.dispose()

    asyncio.run(run())


def test_daily_task_marks_wrong_answer_complete_without_revealing_key():
    async def run():
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        sessions = async_sessionmaker(engine, expire_on_commit=False)
        async with sessions() as session:
            user = User(
                id=1,
                name="Student",
                role=UserRole.STUDENT.value,
                access_code="ABC12345",
            )
            student = Student(
                id=1,
                user_id=1,
                name="Student",
                balance=0,
                hash_access_key="test-key",
                access_code="ABC12345",
            )
            question = DailyTaskQuestion(
                slug="test-question",
                question="Which component emits light?",
                task_type=TaskType.MULTIPLE_CHOICE,
                options=["Resistor", "LED"],
                answer="LED",
            )
            session.add_all([user, student, DailyTask(question=question)])
            await session.commit()

            service = DailyTaskService(session)
            await service.get_or_create(1)
            result = await service.answer(1, "Resistor")
            assert result.correct is False
            assert result.reward == 0
            assert result.balance == 0
            assert "answer" not in result.model_dump()

        await engine.dispose()

    asyncio.run(run())
