
from sqlalchemy.ext.asyncio import AsyncSession
from models.session import Session
from sqlalchemy.future import select

class SessionRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_session(self, student_id: int, token_hash: str) -> Session:
        new_session = Session(student_id=student_id, token_hash=token_hash)
        self.db_session.add(new_session)
        await self.db_session.commit()
        await self.db_session.refresh(new_session)
        return new_session

    async def get_session_by_token(self, token_hash: str) -> Session | None:
        result = await self.db_session.execute(
            select(Session).where(Session.token_hash == token_hash)
        )
        return result.scalars().first()

    async def delete_session(self, token_hash: str) -> None:
        result = await self.db_session.execute(
            select(Session).where(Session.token_hash == token_hash)
        )
        session = result.scalars().first()
        if session:
            await self.db_session.delete(session)
            await self.db_session.commit()

