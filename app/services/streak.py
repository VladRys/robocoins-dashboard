from app.repositories.streak import StreakRepository
from app.models.streak import Streak

class StreakService:
    def __init__(self, streak_repository: StreakRepository):
        self.streak_repository = streak_repository

    async def start_streak(self, student_id: int) -> Streak:
        return await self.streak_repository.start_streak(student_id)

    async def end_streak(self, student_id: int) -> Streak | None:
        return await self.streak_repository.end_streak(student_id)

    async def get_streak(self, student_id: int) -> Streak | None:
        return await self.streak_repository.get_streak(student_id)

    async def get_all_streaks(self) -> list[Streak]:
        return await self.streak_repository.get_all_streaks()

    async def get_longest_streak(self, student_id: int) -> Streak | None:
        return await self.streak_repository.get_longest_streak(student_id)

    async def prolong_streak(self, student_id: int) -> Streak | None:
        return await self.streak_repository.prolong_streak(student_id)

    async def set_streak_days(self, student_id: int, days: int) -> Streak:
        return await self.streak_repository.set_streak_days(student_id, days)