from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.enums import AuthorizationAction, HttpErrorMessage
from app.models.user import User
from app.repositories.course import CourseRepository
from app.repositories.group import GroupRepository
from app.repositories.reward import RewardRepository
from app.repositories.session import SessionRepository
from app.repositories.streak import StreakRepository
from app.repositories.student import StudentRepository
from app.repositories.transaction import TransactionRepository
from app.repositories.users import UserRepository
from app.services.authorization import AuthorizationService
from app.services.balance import BalanceService
from app.services.course import CourseService
from app.services.group import GroupService
from app.services.reward import RewardService
from app.services.session import SessionService
from app.services.streak import StreakService
from app.services.student import StudentService
from app.services.users import UserService


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))


async def get_student_service(db: AsyncSession = Depends(get_db)) -> StudentService:
    return StudentService(db, StudentRepository(db))


def get_session_service(db: AsyncSession = Depends(get_db)) -> SessionService:
    return SessionService(SessionRepository(db))


def get_group_service(db: AsyncSession = Depends(get_db)) -> GroupService:
    return GroupService(db, GroupRepository(db))


def get_course_service(db: AsyncSession = Depends(get_db)) -> CourseService:
    return CourseService(CourseRepository(db))


async def get_reward_service(db: AsyncSession = Depends(get_db)) -> RewardService:
    return RewardService(RewardRepository(db))


def get_balance_service(db: AsyncSession = Depends(get_db)) -> BalanceService:
    return BalanceService(db, StudentRepository(db), TransactionRepository(db))


def get_streak_service(db: AsyncSession = Depends(get_db)) -> StreakService:
    return StreakService(StreakRepository(db))


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
