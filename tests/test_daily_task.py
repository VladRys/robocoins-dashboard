import asyncio
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import func, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base
from app.core.enums import TaskType, UserRole
from app.models.course import Course  # noqa: F401
from app.models.daily_task import DailyTask, DailyTaskQuestion
from app.models.group import Group  # noqa: F401
from app.models.student import Student
from app.models.streak import Streak  # noqa: F401
from app.models.teacher import Teacher  # noqa: F401
from app.models.transaction import BalanceTransaction
from app.models.user import User
from app.services.daily_task import (
    DailyTaskAlreadyCompletedError,
    DailyTaskService,
)


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
