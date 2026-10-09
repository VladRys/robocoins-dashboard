import hashlib
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

    @staticmethod
    def _hash_session_token(session_token: str) -> str:
        return hashlib.sha256(session_token.encode("utf-8")).hexdigest()

    async def create_session(self, student_id: int) -> str:
        session_token = await self._generate_session_token()
        token_hash = self._hash_session_token(session_token)
        await self.repository.create_session(student_id, token_hash)
        return session_token

    async def get_session_by_token(self, session_token: str) -> Session | None:
        token_hash = self._hash_session_token(session_token)
        return await self.repository.get_session_by_token(token_hash)

    async def delete_session(self, session_token: str) -> None:
        token_hash = self._hash_session_token(session_token)
        await self.repository.delete_session(token_hash)

def get_session_service(db_session: AsyncSession = Depends(get_db)) -> SessionService:
    repository = SessionRepository(db_session)
    return SessionService(repository)
