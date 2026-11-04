import asyncio
from pathlib import Path

import pytest
from fastapi import HTTPException
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.routes.balance import (
    change_student_balance,
    get_student_balance_by_id,
    get_student_transaction_history,
)
from app.core.database import Base
from app.core.enums import BalanceChangeReasons
from app.models.course import Course
from app.models.group import Group
from app.models.student import Student
from app.models.user import User
from app.repositories.student import StudentRepository
from app.repositories.transaction import TransactionRepository
from app.schemas.balance import BalanceChangeRequest
from app.services.balance import BalanceService


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

                service = BalanceService(
                    session,
                    StudentRepository(session),
                    TransactionRepository(session),
                )
                empty_history = await get_student_transaction_history(
                    user.id,
                    limit=50,
                    offset=0,
                    service=service,
                )
                assert empty_history.transactions == []
                assert empty_history.status == "success"
                assert empty_history.code == 200

                deposit = None
                for _ in range(10):
                    deposit = await change_student_balance(
                        user.id,
                        BalanceChangeRequest(reason=[BalanceChangeReasons.THEORY]),
                        service,
                    )

                assert deposit is not None
                assert deposit.balance == 10.0
                assert deposit.transaction.operation == "deposit"
                assert deposit.transaction.amount == 1.0

                deduction = await change_student_balance(
                    user.id,
                    BalanceChangeRequest(
                        reason=[
                            BalanceChangeReasons.SERIOUS_VIOLATION,
                            BalanceChangeReasons.DISCIPLINE_BREAKDOWN,
                        ],
                    ),
                    service,
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
                assert len(history.transactions) == 11

                await change_student_balance(
                    user.id,
                    BalanceChangeRequest(
                        reason=[BalanceChangeReasons.SERIOUS_VIOLATION],
                    ),
                    service,
                )

                saved_student = await StudentRepository(session).get_student_by_id(
                    user.id
                )
                saved_transactions = await TransactionRepository(
                    session
                ).get_by_student_id(user.id, limit=50)
                assert saved_student is not None
                assert saved_student.balance == 3.0
                assert len(saved_transactions) == 12
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
