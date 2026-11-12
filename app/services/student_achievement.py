from app.models.achievement import Achievement, StudentAchievement
from app.repositories.achievement import AchievementRepository
from app.repositories.student_achievement import StudentAchievementRepository


class StudentAchievementService:
    def __init__(
        self,
        repository: StudentAchievementRepository,
        achievement_repository: AchievementRepository,
    ) -> None:
        self.repository = repository
        self.achievement_repository = achievement_repository

    async def get_student_achievements(
        self, student_id: int
    ) -> list[StudentAchievement]:
        return await self.repository.get_student_achievements(student_id)

    async def get_coin_earning_progress(
        self,
        student_id: int,
        earned_coins: float,
    ) -> list[tuple[Achievement, bool, float]]:
        achievements = (
            await self.achievement_repository.get_coin_earning_achievements()
        )
        earned_ids = await self.repository.get_student_achievement_ids(student_id)
        progress = []
        for achievement in achievements:
            threshold = achievement.required_coins
            if threshold is None:
                continue
            percent = min(100.0, round(earned_coins / threshold * 100, 2))
            progress.append(
                (achievement, achievement.id in earned_ids, percent)
            )
        return progress

    async def get_earned_daily_task_achievements(
        self,
        student_id: int,
    ) -> list[Achievement]:
        achievements = (
            await self.achievement_repository.get_daily_task_achievements()
        )
        earned_ids = await self.repository.get_student_achievement_ids(student_id)
        return [
            achievement
            for achievement in achievements
            if achievement.id in earned_ids
        ]

    async def get_student_achievement(
        self, student_id: int, achievement_id: int
    ) -> StudentAchievement | None:
        return await self.repository.get_student_achievement(
            student_id,
            achievement_id,
        )

    async def has_achievement(self, student_id: int, achievement_id: int) -> bool:
        return await self.repository.has_achievement(student_id, achievement_id)

    async def add_student_achievement(
        self, student_id: int, achievement_id: int
    ) -> StudentAchievement:
        return await self.repository.add_student_achievement(
            student_id,
            achievement_id,
        )

    async def remove_student_achievement(
        self, student_id: int, achievement_id: int
    ) -> bool:
        return await self.repository.remove_student_achievement(
            student_id,
            achievement_id,
        )

    async def award_coin_earning_achievements(
        self,
        student_id: int,
        earned_coins: float,
    ) -> list[Achievement]:
        achievements = (
            await self.achievement_repository.get_coin_earning_achievements()
        )
        existing_ids = {
            assignment.achievement_id
            for assignment in await self.repository.get_student_achievements(
                student_id
            )
        }
        awarded: list[Achievement] = []
        for achievement in achievements:
            if (
                achievement.id not in existing_ids
                and achievement.required_coins is not None
                and earned_coins >= achievement.required_coins
            ):
                await self.repository.add_student_achievement(
                    student_id,
                    achievement.id,
                    commit=False,
                )
                awarded.append(achievement)
        return awarded
