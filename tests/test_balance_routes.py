import asyncio
from pathlib import Path
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.routes.balance import (
    cancel_student_transaction,
    change_student_balance,
    get_student_balance_by_id,
    get_student_reward_progress,
    get_student_transaction_history,
)
from app.core.database import Base
from app.core.enums import AchievementCategory, AchievementType, BalanceChangeReasons
from app.models.achievement import Achievement
from app.models.course import Course
from app.models.group import Group
from app.models.student import Student
from app.models.user import User
from app.repositories.student import StudentRepository
from app.repositories.achievement import AchievementRepository
from app.repositories.student_achievement import StudentAchievementRepository
from app.repositories.transaction import TransactionRepository
from app.schemas.balance import BalanceChangeRequest
from app.schemas.reward import RewardResponse
from app.services.balance import BalanceService
from app.services.reward import StudentRewardProgress
from app.services.student_achievement import StudentAchievementService


def test_balance_changes_are_atomic_and_recorded_in_history(tmp_path: Path):
    async def run_test():
        engine = create_async_engine(
            URL.create("sqlite+aiosqlite", database=str(tmp_path / "balance.db")),
            pool_pre_ping=True,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        try:
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)

            async with session_factory() as session:
                course = Course(name="Python")
                session.add(course)
                await session.flush()
                group = Group(name="Group A", course_id=course.id)
                session.add(group)
                await session.flush()
                user = User(name="Alex", role="student", access_code="CODE1234")
                session.add(user)
                await session.flush()
                student = Student(
                    id=user.id,
                    user_id=user.id,
                    name="Alex",
                    balance=0.0,
                    hash_access_key="student-hash",
                    access_code="ABC12345",
                    groups=[group],
                )
                session.add(student)
                await session.commit()

                session.add(
                    Achievement(
                        name="Earn three coins",
                        description="Earn three coins",
                        icon="coin",
                        type=AchievementType.BADGE,
                        category=AchievementCategory.COINS_EARNING,
                        required_coins=3,
                    )
                )
                session.add(
                    Achievement(
                        name="Earn eleven coins",
                        description="Earn eleven coins",
                        icon="coin",
                        type=AchievementType.TROPHY,
                        category=AchievementCategory.COINS_EARNING,
                        required_coins=11,
                    )
                )
                await session.commit()
                service = BalanceService(
                    session,
                    StudentRepository(session),
                    TransactionRepository(session),
                    student_achievement_service=StudentAchievementService(
                        StudentAchievementRepository(session),
                        AchievementRepository(session),
                    ),
                )
                authorization = SimpleNamespace(
                    is_allowed=AsyncMock(return_value=True)
                )
                teacher = SimpleNamespace(id=1, role="teacher")
                empty_history = await get_student_transaction_history(
                    user.id,
                    limit=50,
                    offset=0,
                    service=service,
                )
                assert empty_history.transactions == []
                assert empty_history.status == "success"
                assert empty_history.code == 200

                first_deposit = await service.change_balance(
                    user.id,
                    BalanceChangeRequest(reason=[BalanceChangeReasons.THEORY]),
                )
                await service.change_balance(
                    user.id,
                    BalanceChangeRequest(reason=[BalanceChangeReasons.THEORY]),
                )
                assert await StudentAchievementRepository(
                    session
                ).get_student_achievements(user.id) == []

                await service.cancel_transaction(first_deposit[1].id, teacher.id)
                await service.change_balance(
                    user.id,
                    BalanceChangeRequest(reason=[BalanceChangeReasons.THEORY]),
                )
                assert await StudentAchievementRepository(
                    session
                ).get_student_achievements(user.id) == []

                deposit = None
                for _ in range(8):
                    deposit = await change_student_balance(
                        user.id,
                        BalanceChangeRequest(reason=[BalanceChangeReasons.THEORY]),
                        service,
                        authorization=authorization,
                        _user=teacher,
                    )

                assert deposit is not None
                assert deposit.balance == 10.0
                assert deposit.transaction.operation == "deposit"
                assert deposit.transaction.amount == 1.0
                awarded = await StudentAchievementRepository(
                    session
                ).get_student_achievements(user.id)
                assert len(awarded) == 1
                assert awarded[0].achievement_id == 1

                deduction = await change_student_balance(
                    user.id,
                    BalanceChangeRequest(
                        reason=[
                            BalanceChangeReasons.SERIOUS_VIOLATION,
                            BalanceChangeReasons.DISCIPLINE_BREAKDOWN,
                        ],
                    ),
                    service,
                    authorization=authorization,
                    _user=teacher,
                )

                assert deduction.balance == 6.0
                assert deduction.transaction.operation == "deduct"
                assert deduction.transaction.amount == 4.0
                assert (
                    await get_student_balance_by_id(user.id, service)
                ).balance == 6.0

                history = await get_student_transaction_history(
                    user.id,
                    limit=50,
                    offset=0,
                    service=service,
                )
                assert [item.operation for item in history.transactions[:2]] == [
                    "deduct",
                    "deposit",
                ]
                assert history.transactions[1].reason == [
                    BalanceChangeReasons.THEORY.value,
                ]
                assert len(history.transactions) == 12

                group_result = await service.award_group_practice_completed(
                    group.id
                )
                assert group_result is not None
                assert len(group_result[1]) == 1
                assert group_result[1][0][0] == 7.0
                awarded = await StudentAchievementRepository(
                    session
                ).get_student_achievements(user.id)
                assert {assignment.achievement_id for assignment in awarded} == {
                    1,
                    2,
                }

                await change_student_balance(
                    user.id,
                    BalanceChangeRequest(
                        reason=[BalanceChangeReasons.SERIOUS_VIOLATION],
                    ),
                    service,
                    authorization=authorization,
                    _user=teacher,
                )

                saved_student = await StudentRepository(session).get_student_by_id(
                    user.id
                )
                saved_transactions = await TransactionRepository(
                    session
                ).get_by_student_id(user.id, limit=50)
                assert saved_student is not None
                assert saved_student.balance == 4.0
                assert len(saved_transactions) == 14
                assert len(
                    await StudentAchievementRepository(session).get_student_achievements(
                        user.id
                    )
                ) == 2
        finally:
            await engine.dispose()

    asyncio.run(run_test())


def test_balance_endpoints_return_404_for_unknown_student(tmp_path: Path):
    async def run_test():
        engine = create_async_engine(
            URL.create("sqlite+aiosqlite", database=str(tmp_path / "missing.db")),
            pool_pre_ping=True,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        try:
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)

            async with session_factory() as session:
                service = BalanceService(
                    session,
                    StudentRepository(session),
                    TransactionRepository(session),
                )

                with pytest.raises(HTTPException) as error:
                    await get_student_balance_by_id(999999, service)
                assert error.value.status_code == 404

                with pytest.raises(HTTPException) as error:
                    await get_student_transaction_history(
                        999999,
                        limit=50,
                        offset=0,
                        service=service,
                    )
                assert error.value.status_code == 404
        finally:
            await engine.dispose()

    asyncio.run(run_test())


def test_reward_progress_uses_current_goal():
    student = SimpleNamespace(balance=40.0, current_goal="Python course")
    student_service = SimpleNamespace(
        get_student_by_id=AsyncMock(return_value=student)
    )
    goal_reward = SimpleNamespace(
        id=42,
        name="Python course",
        price=100,
        description="A course reward",
        type="reward",
        course_category=None,
    )
    rewards_service = SimpleNamespace(
        get_student_reward_progress=AsyncMock(
            return_value=StudentRewardProgress(
                current_goal=goal_reward,
                coins_remaining=60.0,
                progress_percent=40.0,
            )
        )
    )

    response = asyncio.run(
        get_student_reward_progress(
            123,
            student_service=student_service,
            rewards_service=rewards_service,
        )
    )

    assert response.current_goal == RewardResponse.model_validate(goal_reward)
    assert response.balance == 40.0
    assert response.coins_remaining == 60.0
    assert response.progress_percent == 40.0
    rewards_service.get_student_reward_progress.assert_awaited_once_with(
        student_id=123,
        balance=40.0,
        current_goal="Python course",
        current_goal_reward_id=None,
    )


def test_balance_updates_compile_with_postgres_rounding():
    from sqlalchemy.dialects import postgresql

    async def run_test():
        session = SimpleNamespace(
            execute=AsyncMock(
                return_value=SimpleNamespace(scalar_one_or_none=lambda: 1.1)
            )
        )
        repository = StudentRepository(cast(AsyncSession, session))

        assert await repository.change_balance(1, 0.1) == 1.1
        change_sql = str(
            session.execute.await_args.args[0].compile(
                dialect=postgresql.dialect()
            )
        )
        assert "round(CAST(students.balance +" in change_sql
        assert "round(students.balance +" not in change_sql

        await repository.reverse_balance_transaction(1, "deduct", 0.1)
        reverse_sql = str(
            session.execute.await_args.args[0].compile(
                dialect=postgresql.dialect()
            )
        )
        assert "round(CAST(students.balance +" in reverse_sql
        assert "round(students.balance +" not in reverse_sql

    asyncio.run(run_test())


def test_admin_can_cancel_transaction_through_api(tmp_path: Path):
    async def run_test():
        engine = create_async_engine(
            URL.create(
                "sqlite+aiosqlite",
                database=str(tmp_path / "cancel-transaction.db"),
            )
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        try:
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)

            async with session_factory() as session:
                admin = User(
                    name="Admin",
                    role="admin",
                    access_code="ADMIN123",
                )
                student_user = User(
                    name="Student",
                    role="student",
                    access_code="STUDENT123",
                )
                session.add_all([admin, student_user])
                await session.flush()
                session.add(
                    Student(
                        id=student_user.id,
                        user_id=student_user.id,
                        name=student_user.name,
                        hash_access_key="student-hash",
                        access_code="STUDENT456",
                        balance=5.0,
                    )
                )
                await session.commit()

                service = BalanceService(
                    session,
                    StudentRepository(session),
                    TransactionRepository(session),
                )
                _, transaction = await service.change_balance(
                    student_user.id,
                    BalanceChangeRequest(reason=[BalanceChangeReasons.THEORY]),
                )
                authorization = SimpleNamespace(
                    is_allowed=AsyncMock(return_value=True)
                )

                result = await cancel_student_transaction(
                    transaction.id,
                    service,
                    admin,
                    authorization,
                )

                assert result.balance == 5.0
                assert result.transaction.cancelled_at is not None
                assert result.transaction.cancelled_by_user_id == admin.id
                authorization.is_allowed.assert_awaited_once()

                with pytest.raises(HTTPException) as error:
                    await cancel_student_transaction(
                        transaction.id,
                        service,
                        admin,
                        authorization,
                    )
                assert error.value.status_code == 409
        finally:
            await engine.dispose()

    asyncio.run(run_test())
