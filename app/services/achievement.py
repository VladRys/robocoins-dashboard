from app.core.enums import AchievementType
from app.models.achievement import Achievement
from app.repositories.achievement import AchievementRepository


class AchievementService:
    def __init__(self, repository: AchievementRepository) -> None:
        self.repository = repository

    async def get_achievement_by_id(self, achievement_id: int) -> Achievement | None:
        return await self.repository.get_achievement_by_id(achievement_id)

    async def get_all_achievements(self) -> list[Achievement]:
        return await self.repository.get_all_achievements()

    async def get_coin_earning_achievements(self) -> list[Achievement]:
        return await self.repository.get_coin_earning_achievements()

    async def get_achievements_by_category(
        self, category: str
    ) -> list[Achievement]:
        return await self.repository.get_achievements_by_category(category)

    async def get_achievements_by_type(
        self, achievement_type: AchievementType
    ) -> list[Achievement]:
        return await self.repository.get_achievements_by_type(achievement_type)

    async def create_achievement(self, achievement: Achievement) -> Achievement:
        return await self.repository.create_achievement(achievement)

    async def update_achievement(
        self,
        achievement_id: int,
        *,
        name: str | None = None,
        description: str | None = None,
        icon: str | None = None,
        achievement_type: AchievementType | None = None,
        category: str | None = None,
        required_coins: int | None = None,
    ) -> Achievement | None:
        return await self.repository.update_achievement(
            achievement_id,
            name=name,
            description=description,
            icon=icon,
            achievement_type=achievement_type,
            category=category,
            required_coins=required_coins,
        )

    async def delete_achievement(self, achievement_id: int) -> bool:
        return await self.repository.delete_achievement(achievement_id)
