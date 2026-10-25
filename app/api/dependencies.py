from fastapi import Depends, HTTPException, Request

from app.core.enums import AuthorizationAction, HttpErrorMessage
from app.models.user import User
from app.services.authorization import AuthorizationService
from app.services.group import GroupService, get_group_service
from app.services.session import SessionService, get_session_service
from app.services.student import StudentService, get_student_service
from app.services.users import UserService, get_user_service


async def get_authenticated_user(
    request: Request,
    session_service: SessionService = Depends(get_session_service),
    user_service: UserService = Depends(get_user_service),
) -> User:
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail=HttpErrorMessage.NOT_AUTHENTICATED)

    session = await session_service.get_session_by_token(token)
    if session is None:
        raise HTTPException(status_code=401, detail=HttpErrorMessage.INVALID_SESSION_TOKEN)
    if session.is_expired():
        await session_service.delete_session(token)
        raise HTTPException(status_code=401, detail=HttpErrorMessage.SESSION_EXPIRED)

    user = await user_service.get_user_by_id(session.user_id)
    if user is None:
        raise HTTPException(status_code=401, detail=HttpErrorMessage.USER_NOT_FOUND)
    return user


async def get_authorization_service(
    student_service: StudentService = Depends(get_student_service),
    group_service: GroupService = Depends(get_group_service),
) -> AuthorizationService:
    return AuthorizationService(student_service, group_service)


async def get_authenticated_teacher(
    user: User = Depends(get_authenticated_user),
    authorization: AuthorizationService = Depends(get_authorization_service),
) -> User:
    if not await authorization.is_allowed(AuthorizationAction.TEACHER_OPERATION, user):
        raise HTTPException(status_code=403, detail=HttpErrorMessage.ONLY_TEACHERS_CAN_MODIFY)
    return user


async def get_authenticated_admin(
    user: User = Depends(get_authenticated_user),
    authorization: AuthorizationService = Depends(get_authorization_service),
) -> User:
    if not await authorization.is_allowed(AuthorizationAction.ADMINISTRATOR_OPERATION, user):
        raise HTTPException(status_code=403, detail="Administrator access required")
    return user
