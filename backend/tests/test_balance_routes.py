import asyncio
import sys
from pathlib import Path

import pytest
from fastapi import HTTPException
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from api.routes.balance import (
    change_student_balance,
    get_student_balance_by_id,
    get_student_transaction_history,
)
from app.core.database import Base
from models.course import Course
from models.group import Group
from models.student import Student
from repositories.student import StudentRepository
from repositories.transaction import TransactionRepository
from schemas.balance import BalanceChangeRequest
from services.balance import BalanceService


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
                session.add(
                    Student(
                        id=123456,
                        name="Alex",
                        group_id=group.id,
                        course_name=course.name,
                        balance=0,
                        hash_access_key="student-hash",
                        access_code="ABC12345",
                    )
                )
                await session.commit()

                service = BalanceService(
                    session,
                    StudentRepository(session),
                    TransactionRepository(session),
                )
                empty_history = await get_student_transaction_history(
                    123456,
                    limit=50,
                    offset=0,
                    service=service,
                )
                assert empty_history.transactions == []
                assert empty_history.status == "success"
                assert empty_history.code == 200

                deposit = await change_student_balance(
                    123456,
                    BalanceChangeRequest(
                        operation="deposit",
                        amount=10,
                        reason="Completed a challenge",
                    ),
                    service,
                )
                deduction = await change_student_balance(
                    123456,
                    BalanceChangeRequest(operation="deduct", amount=4),
                    service,
                )

                assert deposit.balance == 10
                assert deposit.transaction.operation == "deposit"
                assert deposit.transaction.amount == 10
                assert deduction.balance == 6
                assert deduction.transaction.operation == "deduct"
                assert (await get_student_balance_by_id(123456, service)).balance == 6

                history = await get_student_transaction_history(
                    123456,
                    limit=50,
                    offset=0,
                    service=service,
                )
                assert [item.operation for item in history.transactions] == [
                    "deduct",
                    "deposit",
                ]
                assert history.transactions[1].reason == "Completed a challenge"
                assert len(history.transactions) == 2

                with pytest.raises(HTTPException) as error:
                    await change_student_balance(
                        123456,
                        BalanceChangeRequest(operation="deduct", amount=7),
                        service,
                    )
                assert error.value.status_code == 409

                saved_student = await StudentRepository(session).get_student_by_id(
                    123456
                )
                saved_transactions = await TransactionRepository(
                    session
                ).get_by_student_id(123456, limit=50)
                assert saved_student is not None
                assert saved_student.balance == 6
                assert len(saved_transactions) == 2
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