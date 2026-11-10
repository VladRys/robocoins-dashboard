from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import BalanceTransaction


class TransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self) -> None:
        await self.session.commit()

    async def create(self, transaction: BalanceTransaction) -> BalanceTransaction:
        self.session.add(transaction)
        await self.session.flush()
        return transaction

    async def get_by_id_for_update(
        self,
        transaction_id: int,
    ) -> BalanceTransaction | None:
        result = await self.session.execute(
            select(BalanceTransaction)
            .where(BalanceTransaction.id == transaction_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def get_by_student_id(
        self, student_id: int, limit: int, offset: int = 0
    ) -> list[BalanceTransaction]:
        result = await self.session.execute(
            select(BalanceTransaction)
            .where(BalanceTransaction.student_id == student_id)
            .order_by(
                BalanceTransaction.created_at.desc(),
                BalanceTransaction.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_total_earned_coins(self, student_id: int) -> float:
        total = await self.session.scalar(
            select(func.coalesce(func.sum(BalanceTransaction.amount), 0)).where(
                BalanceTransaction.student_id == student_id,
                BalanceTransaction.operation == "deposit",
                BalanceTransaction.cancelled_at.is_(None),
            )
        )
        return float(total if total is not None else 0)
