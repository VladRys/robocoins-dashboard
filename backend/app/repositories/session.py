
from sqlalchemy.ext.asyncio import AsyncSession
from models.session import Session
from sqlalchemy.future import select

class SessionRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_session(self, student_id: int, session_token: str) -> Session:
        new_session = Session(student_id=student_id, session_token=session_token)
        self.db_session.add(new_session)
        await self.db_session.commit()
        await self.db_session.refresh(new_session)
        return new_session

    async def get_session_by_token(self, session_token: str) -> Session:
        result = await self.db_session.execute(
            select(Session).where(Session.session_token == session_token)
        )
        return result.scalars().first()

    async def delete_session(self, session_token: str):
        result = await self.db_session.execute(
            select(Session).where(Session.session_token == session_token)
        )
        session = result.scalars().first()
        if session:
            await self.db_session.delete(session)
            await self.db_session.commit()


