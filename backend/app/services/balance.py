from datetime import datetime, timezone

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from models.transaction import BalanceTransaction
from repositories.student import StudentRepository
from repositories.transaction import TransactionRepository
from schemas.balance import BalanceChangeRequest

class StudentNotFoundError(Exception):
    pass


class TransactionNotFoundError(Exception):
    pass


class TransactionAlreadyCancelledError(Exception):
    pass


class InsufficientBalanceToCancelError(Exception):
    pass


class BalanceService:
    def __init__(
        self,
        session: AsyncSession,
        student_repository: StudentRepository,
        transaction_repository: TransactionRepository,
    ):
        self.session = session
        self.student_repository = student_repository
        self.transaction_repository = transaction_repository

    async def get_balance(self, student_id: int) -> int:
        student = await self.student_repository.get_student_by_id(student_id)
        if student is None:
            raise StudentNotFoundError
        return student.balance

    async def change_balance(
        self, student_id: int, change: BalanceChangeRequest
    ) -> tuple[int, BalanceTransaction]:
        signed_amount = sum(reason.balance_delta for reason in change.reason)
        operation = "deposit" if signed_amount > 0 else "deduct"
        amount = abs(signed_amount)
        balance = await self.student_repository.change_balance(
            student_id,
            signed_amount,
        )
        if balance is None:
            raise StudentNotFoundError

        transaction = BalanceTransaction(
            student_id=student_id,
            operation=operation,
            amount=amount,
            reason=[reason.value for reason in change.reason],
        )
        await self.transaction_repository.create(transaction)
        await self.session.commit()
        return balance, transaction

    async def get_history(
        self, student_id: int, limit: int, offset: int = 0
    ) -> list[BalanceTransaction]:
        if await self.student_repository.get_student_by_id(student_id) is None:
            raise StudentNotFoundError
        return await self.transaction_repository.get_by_student_id(
            student_id,
            limit,
            offset,
        )

    async def cancel_transaction(
        self,
        transaction_id: int,
        cancelled_by_user_id: int,
    ) -> tuple[int, BalanceTransaction]:
        transaction = await self.transaction_repository.get_by_id_for_update(
            transaction_id
        )
        if transaction is None:
            raise TransactionNotFoundError
        if transaction.cancelled_at is not None:
            raise TransactionAlreadyCancelledError

        balance = await self.student_repository.reverse_balance_transaction(
            transaction.student_id,
            transaction.operation,
            transaction.amount,
        )
        if balance is None:
            raise InsufficientBalanceToCancelError

        transaction.cancelled_at = datetime.now(timezone.utc)
        transaction.cancelled_by_user_id = cancelled_by_user_id
        await self.session.commit()
        return balance, transaction


def get_balance_service(session: AsyncSession = Depends(get_db)) -> BalanceService:
    return BalanceService(
        session,
        StudentRepository(session),
        TransactionRepository(session),
    )
