from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AchievementCategory, AchievementType
from app.models.achievement import Achievement


class AchievementRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_achievement_by_id(self, achievement_id: int) -> Achievement | None:
        return await self.session.get(Achievement, achievement_id)

    async def get_all_achievements(self) -> list[Achievement]:
        result = await self.session.execute(
            select(Achievement).order_by(Achievement.id)
        )
        return list(result.scalars().all())

    async def get_all_coin_earning_achievements(self) -> list[Achievement]:
        return await self.get_coin_earning_achievements()

    async def get_achievements_by_category(self, category: str) -> list[Achievement]:
        result = await self.session.execute(
            select(Achievement)
            .where(Achievement.category == category)
            .order_by(Achievement.id)
        )
        return list(result.scalars().all())

    async def get_coin_earning_achievements(self) -> list[Achievement]:
        result = await self.session.execute(
            select(Achievement)
            .where(
                Achievement.category == AchievementCategory.COINS_EARNING,
                Achievement.required_coins.is_not(None),
            )
            .order_by(Achievement.required_coins, Achievement.id)
        )
        return list(result.scalars().all())

    async def get_daily_task_achievements(self) -> list[Achievement]:
        result = await self.session.execute(
            select(Achievement)
            .where(
                Achievement.category.in_(
                    (
                        AchievementCategory.DAILY_TASK_STREAK,
                        AchievementCategory.DAILY_TASK_COMPLETION,
                    )
                )
            )
            .order_by(Achievement.id)
        )
        return list(result.scalars().all())

    async def get_achievements_by_type(
        self, achievement_type: AchievementType
    ) -> list[Achievement]:
        result = await self.session.execute(
            select(Achievement)
            .where(Achievement.type == achievement_type)
            .order_by(Achievement.id)
        )
        return list(result.scalars().all())

    async def create_achievement(self, achievement: Achievement) -> Achievement:
        self.session.add(achievement)
        await self.session.commit()
        await self.session.refresh(achievement)
        return achievement

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
        achievement = await self.get_achievement_by_id(achievement_id)
        if achievement is None:
            return None

        if name is not None:
            achievement.name = name
        if description is not None:
            achievement.description = description
        if icon is not None:
            achievement.icon = icon
        if achievement_type is not None:
            achievement.type = achievement_type
        if category is not None:
            achievement.category = category
        if required_coins is not None:
            achievement.required_coins = required_coins

        await self.session.commit()
        return achievement

    async def delete_achievement(self, achievement_id: int) -> bool:
        achievement = await self.get_achievement_by_id(achievement_id)
        if achievement is None:
            return False

        await self.session.delete(achievement)
        await self.session.commit()
        return True
