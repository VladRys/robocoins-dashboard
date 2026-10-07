from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Request, HTTPException

from app.services.student import StudentService, get_student_service
from models.session import Session

class AuthService:
    def __init__(self, db_session: AsyncSession, student_service: StudentService = Depends(get_student_service), session_service):
        self.db_session = db_session
        self.student_service = student_service
        self.session_service = session_service

    async def verify_code(self, name: str, code: str) -> bool:
        student = await self.student_service.get_student_by_name(name)

        if code != student.access_code:
            return False

        return True

    async def get_current_student(self, request: Request) -> Student:
        token = request.cookies.get("session")

        if not token:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated",
            )

        session = self.session_service.get_session_by_token(self.db_session, token)

        if not session:
            raise HTTPException(
                status_code=401,
                detail="Invalid session",
            )

        if session.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=401,
                detail="Session expired",
            )

        return session.student

def get_auth_service(db_session: AsyncSession = Depends(get_db), student_service: StudentService = Depends(get_student_service), session_service: SessionService = Depends(get_session_service)) -> AuthService:
    return AuthService(db_session, student_service, session_service)
