from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import reward
from app.repositories.reward import RewardRepository
from models.reward import Reward
from core.database import get_db


class RewardService:
    def __init__(self, repository: RewardRepository) -> None:
        self.repository = repository

    async def get_reward_by_id(self, reward_id: int) -> Reward | None:
        return await self.repository.get_reward_by_id(reward_id)

    async def get_reward_by_name(self, reward_name: str) -> Reward | None:
        return await self.repository.get_reward_by_name(reward_name)

    async def get_all_rewards(self) -> list[Reward]:
        return await self.repository.get_all_rewards()

async def get_reward_service(self, db: AsyncSession = Depends(get_db)) -> RewardService:
    return RewardService(RewardRepository(db))
