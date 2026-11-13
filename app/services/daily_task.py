from app.repositories.daily_task import (
    DailyTaskAlreadyCompletedError,
    DailyTaskNotFoundError,
    DailyTaskRepository,
    StudentNotFoundError,
)
from app.repositories.achievement import AchievementRepository
from app.repositories.student_achievement import StudentAchievementRepository
from app.repositories.transaction import TransactionRepository
from app.services.student_achievement import StudentAchievementService
from datetime import date

from app.schemas.daily_task import (
    DailyTaskAnswerResponse,
    DailyTaskResponse,
    DailyTaskTestAnswerResponse,
    DailyTaskTestResponse,
)


class DailyTaskService:
    def __init__(self, repository):
        self.repository = (
            repository if isinstance(repository, DailyTaskRepository)
            else DailyTaskRepository(repository)
        )
        session = self.repository.session
        self.transaction_repository = TransactionRepository(session)
        self.student_achievement_service = StudentAchievementService(
            StudentAchievementRepository(session),
            AchievementRepository(session),
        )

    async def get_test_tasks(self) -> list[DailyTaskTestResponse]:
        return await self.repository.get_test_tasks()

    async def answer_test_task(self, task_id: int, answer: str) -> DailyTaskTestAnswerResponse:
        return await self.repository.answer_test_task(task_id, answer)

    async def get_or_create(self, student_id: int) -> DailyTaskResponse:
        self.repository.current_date = date.today
        return await self.repository.get_or_create(student_id)

    async def get_or_create_all(self, student_id: int) -> list[DailyTaskResponse]:
        self.repository.current_date = date.today
        return await self.repository.get_or_create_all(student_id)

    async def answer(self, student_id: int, answer: str, *, course_id: int | None = None) -> DailyTaskAnswerResponse:
        self.repository.current_date = date.today
        result = await self.repository.answer(student_id, answer, course_id=course_id)
        if result.correct:
            earned_coins = await self.transaction_repository.get_total_earned_coins(
                student_id
            )
            await self.student_achievement_service.award_coin_earning_achievements(
                student_id,
                earned_coins,
            )
        await self.transaction_repository.commit()
        return result

    async def _get_assignment(self, *args, **kwargs):
        return await self.repository._get_assignment(*args, **kwargs)

