from datetime import datetime, timezone

from app.core.enums import BalanceChangeReasons
from app.models.group import Group
from app.repositories.group import GroupRepository
from app.models.transaction import BalanceTransaction
from app.repositories.student import StudentRepository
from app.repositories.transaction import TransactionRepository
from app.schemas.balance import BalanceChangeRequest

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
        session,
        student_repository: StudentRepository,
        transaction_repository: TransactionRepository,
        group_repository: GroupRepository | None = None,
    ):
        self.student_repository = student_repository
        self.transaction_repository = transaction_repository
        self.group_repository = group_repository or GroupRepository(
            student_repository.session
        )

    async def get_balance(self, student_id: int) -> float:
        student = await self.student_repository.get_student_by_id(student_id)
        if student is None:
            raise StudentNotFoundError
        return student.balance

    async def change_balance(
        self, student_id: int, change: BalanceChangeRequest
    ) -> tuple[float, BalanceTransaction]:
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
        await self.transaction_repository.commit()
        return balance, transaction

    async def award_group_practice_completed(
        self, group_id: int
    ) -> tuple[Group, list[tuple[float, BalanceTransaction]]] | None:
        """Award one practice-completed coin to every current group member."""
        group = await self.group_repository.get_group_by_id(group_id)
        if group is None:
            return None

        student_ids = await self.group_repository.get_group_student_ids(group_id)
        results: list[tuple[float, BalanceTransaction]] = []
        for student_id in student_ids:
            balance = await self.student_repository.change_balance(student_id, 1.0)
            if balance is None:
                continue
            transaction = BalanceTransaction(
                student_id=student_id,
                operation="deposit",
                amount=1.0,
                reason=[BalanceChangeReasons.PRACTICE_COMPLETED.value],
            )
            await self.transaction_repository.create(transaction)
            results.append((balance, transaction))

        await self.transaction_repository.commit()
        return group, results

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
    ) -> tuple[float, BalanceTransaction]:
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
        await self.transaction_repository.commit()
        return balance, transaction


