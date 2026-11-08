from app.repositories.daily_task import (
    DailyTaskAlreadyCompletedError,
    DailyTaskNotFoundError,
    DailyTaskRepository,
    StudentNotFoundError,
)
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
        return await self.repository.answer(student_id, answer, course_id=course_id)

    async def _get_assignment(self, *args, **kwargs):
        return await self.repository._get_assignment(*args, **kwargs)

