from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import BalanceTransaction


class TransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, transaction: BalanceTransaction) -> BalanceTransaction:
        self.session.add(transaction)
        await self.session.flush()
        return transaction

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
