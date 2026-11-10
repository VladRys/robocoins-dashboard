import asyncio
from unittest.mock import AsyncMock

from app.core.enums import AchievementType
from app.models.achievement import Achievement, StudentAchievement
from app.services.achievement import AchievementService
from app.services.student_achievement import StudentAchievementService


def test_achievement_service_delegates_repository_operations():
    async def run():
        repository = AsyncMock()
        repository.get_achievement_by_id.return_value = None
        repository.get_all_achievements.return_value = []
        repository.get_achievements_by_category.return_value = []
        repository.get_achievements_by_type.return_value = []
        repository.update_achievement.return_value = None
        repository.delete_achievement.return_value = False
        achievement = Achievement(
            name="First steps",
            description="Complete an activity",
            icon="star",
            type=AchievementType.BADGE,
            category="progress",
        )
        repository.create_achievement.return_value = achievement
        service = AchievementService(repository)

        assert await service.get_achievement_by_id(1) is None
        assert await service.get_all_achievements() == []
        assert await service.get_achievements_by_category("progress") == []
        assert await service.get_achievements_by_type(AchievementType.BADGE) == []
        assert await service.create_achievement(achievement) is achievement
        assert await service.update_achievement(
            1,
            name="Updated",
            achievement_type=AchievementType.TROPHY,
            required_coins=10,
        ) is None
        assert await service.delete_achievement(1) is False

        repository.get_achievement_by_id.assert_awaited_once_with(1)
        repository.get_all_achievements.assert_awaited_once_with()
        repository.get_achievements_by_category.assert_awaited_once_with("progress")
        repository.get_achievements_by_type.assert_awaited_once_with(
            AchievementType.BADGE
        )
        repository.create_achievement.assert_awaited_once_with(achievement)
        repository.update_achievement.assert_awaited_once_with(
            1,
            name="Updated",
            description=None,
            icon=None,
            achievement_type=AchievementType.TROPHY,
            category=None,
            required_coins=10,
        )
        repository.delete_achievement.assert_awaited_once_with(1)

    asyncio.run(run())


def test_student_achievement_service_delegates_repository_operations():
    async def run():
        repository = AsyncMock()
        achievement_repository = AsyncMock()
        achievement_repository.get_coin_earning_achievements.return_value = []
        repository.get_student_achievements.return_value = []
        repository.get_student_achievement.return_value = None
        repository.has_achievement.return_value = False
        assignment = StudentAchievement(student_id=1, achievement_id=2)
        repository.add_student_achievement.return_value = assignment
        repository.remove_student_achievement.return_value = True
        service = StudentAchievementService(repository, achievement_repository)

        assert await service.get_student_achievements(1) == []
        assert await service.get_student_achievement(1, 2) is None
        assert not await service.has_achievement(1, 2)
        assert await service.add_student_achievement(1, 2) is assignment
        assert await service.remove_student_achievement(1, 2)

        repository.get_student_achievements.assert_awaited_once_with(1)
        repository.get_student_achievement.assert_awaited_once_with(1, 2)
        repository.has_achievement.assert_awaited_once_with(1, 2)
        repository.add_student_achievement.assert_awaited_once_with(1, 2)
        repository.remove_student_achievement.assert_awaited_once_with(1, 2)

    asyncio.run(run())


def test_coin_earning_achievements_are_awarded_once_when_threshold_is_reached():
    async def run():
        repository = AsyncMock()
        repository.get_student_achievements.return_value = []
        repository.add_student_achievement.return_value = StudentAchievement(
            student_id=1,
            achievement_id=2,
        )
        achievement_repository = AsyncMock()
        achievement = Achievement(
            id=2,
            name="Coin collector",
            description="Earn 10 coins",
            icon="coin",
            type=AchievementType.BADGE,
            category="coins_earning",
            required_coins=10,
        )
        achievement_repository.get_coin_earning_achievements.return_value = [
            achievement
        ]
        service = StudentAchievementService(repository, achievement_repository)

        assert await service.award_coin_earning_achievements(1, 9) == []
        repository.add_student_achievement.assert_not_awaited()

        assert await service.award_coin_earning_achievements(1, 10) == [achievement]
        repository.add_student_achievement.assert_awaited_once_with(
            1,
            2,
            commit=False,
        )

        repository.get_student_achievements.return_value = [
            StudentAchievement(student_id=1, achievement_id=2)
        ]
        assert await service.award_coin_earning_achievements(1, 20) == []
        repository.add_student_achievement.assert_awaited_once()

    asyncio.run(run())
