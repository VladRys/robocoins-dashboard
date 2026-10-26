import asyncio

from app.api.dependencies import (
    get_balance_service,
    get_course_service,
    get_group_service,
    get_reward_service,
    get_session_service,
    get_streak_service,
    get_student_service,
    get_user_service,
)
from app.repositories.streak import StreakRepository
from app.services.balance import BalanceService
from app.services.course import CourseService
from app.services.group import GroupService
from app.services.reward import RewardService
from app.services.session import SessionService
from app.services.streak import StreakService
from app.services.student import StudentService
from app.services.users import UserService


def test_service_dependencies_build_services_from_the_supplied_session():
    async def run():
        db = object()
        assert isinstance(get_user_service(db), UserService)
        student_service = await get_student_service(db)
        assert isinstance(student_service, StudentService)
        assert student_service.db is db

        session_service = get_session_service(db)
        assert isinstance(session_service, SessionService)
        assert isinstance(get_group_service(db), GroupService)
        assert isinstance(get_course_service(db), CourseService)
        assert isinstance(await get_reward_service(db), RewardService)
        assert isinstance(get_balance_service(db), BalanceService)

        streak_service = get_streak_service(db)
        assert isinstance(streak_service, StreakService)
        assert isinstance(streak_service.streak_repository, StreakRepository)
        assert streak_service.streak_repository.db is db

    asyncio.run(run())
