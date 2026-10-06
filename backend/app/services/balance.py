from backend.app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import BalanceTransaction
from repositories.student import StudentRepository
from repositories.transaction import TransactionRepository
from schemas.balance import BalanceChangeRequest

from fastapi import Depends 

class StudentNotFoundError(Exception):
    pass


class InsufficientBalanceError(Exception):
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
        signed_amount = change.amount
        if change.operation == "deduct":
            signed_amount = -change.amount
        balance = await self.student_repository.change_balance(
            student_id,
            signed_amount,
        )
        if balance is None:
            student = await self.student_repository.get_student_by_id(student_id)
            if student is None:
                raise StudentNotFoundError
            raise InsufficientBalanceError

        transaction = BalanceTransaction(
            student_id=student_id,
            operation=change.operation,
            amount=change.amount,
            reason=change.reason,
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
        
def get_balance_service(session: AsyncSession = Depends(get_db)) -> BalanceService:
    return BalanceService(
        session,
        StudentRepository(session),
        TransactionRepository(session),
    )