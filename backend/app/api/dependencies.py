from fastapi import Depends, HTTPException, Request

from app.core.enums import UserRole
from models.user import User
from services.session import SessionService, get_session_service
from services.users import UserService, get_user_service


async def get_authenticated_user(
    request: Request,
    session_service: SessionService = Depends(get_session_service),
    user_service: UserService = Depends(get_user_service),
) -> User:
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session = await session_service.get_session_by_token(token)
    if session is None:
        raise HTTPException(status_code=401, detail="Invalid session token")
    if session.is_expired():
        await session_service.delete_session(token)
        raise HTTPException(status_code=401, detail="Session expired")

    user = await user_service.get_user_by_id(session.user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


async def get_authenticated_teacher(
    user: User = Depends(get_authenticated_user),
) -> User:
    if user.role != UserRole.TEACHER.value:
        raise HTTPException(status_code=403, detail="Only teachers can modify this resource")
    return user
