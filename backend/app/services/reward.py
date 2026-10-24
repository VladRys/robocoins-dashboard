from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.reward import Reward
from app.core.enums import CourseCategory
from app.repositories.reward import RewardRepository
from app.core.database import get_db


class RewardService:
    def __init__(self, repository: RewardRepository) -> None:
        self.repository = repository

    async def create_reward(self, reward: Reward) -> Reward:
        return await self.repository.create_reward(reward)
    
    async def remove_reward(self, reward_id: int):
        await self.repository.remove_reward(reward_id)
        return

    async def get_reward_by_id(self, reward_id: int) -> Reward | None:
        return await self.repository.get_reward_by_id(reward_id)

    async def get_reward_by_name(self, reward_name: str) -> Reward | None:
        return await self.repository.get_reward_by_name(reward_name)

    async def get_all_rewards(self, course_category: CourseCategory | None = None) -> list[Reward]:
        return await self.repository.get_all_rewards(course_category)

    async def get_rewards_for_student(self, student_id: int) -> list[Reward]:
        return await self.repository.get_rewards_for_student(student_id)

async def get_reward_service(db: AsyncSession = Depends(get_db)) -> RewardService:
    return RewardService(RewardRepository(db))
