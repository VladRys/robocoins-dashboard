import secrets
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from models.session import Session
from repositories.session import SessionRepository

class SessionService:
    def __init__(self, repository: SessionRepository):
        self.repository = repository

    async def _generate_session_token(self) -> str:
        return secrets.token_hex(32)

    async def create_session(self, student_id: int) -> Session:
        session_token = await self._generate_session_token()
        return await self.repository.create_session(student_id, session_token)

    async def get_session_by_token(self, session_token: str) -> Session:
        return await self.repository.get_session_by_token(session_token)

    async def delete_session(self, session_token: str):
        return await self.repository.delete_session(session_token)

def get_session_service(db_session: AsyncSession = Depends(get_db)) -> SessionService:
    repository = SessionRepository(db_session)
    return SessionService(repository)

