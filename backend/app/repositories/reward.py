from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.reward import Reward

class RewardRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_reward(self, reward: Reward) -> Reward:
        self.session.add(reward)
        await self.session.commit()
        created_reward = await self.get_reward_by_id(reward.id)
        if created_reward is None:
            raise RuntimeError("Reward was not available after being created")
        
        return created_reward

    async def remove_reward(self, reward_id: int):
        reward = await self.get_reward_by_id(reward_id)
        if reward:
            await self.session.delete(reward)
            await self.session.commit()

    async def get_reward_by_id(self, reward_id: int) -> Reward | None:
        return await self.session.get(Reward, reward_id)

    async def get_reward_by_name(self, reward_name: str) -> Reward:
        result = await self.session.execute(
            select(Reward).where(Reward.name == reward_name)
        )
        return result.scalar_one_or_none()

    async def get_all_rewards(self) -> list[Reward]:
        rewards = await self.session.execute(select(Reward).order_by(Reward.price))
        return list(rewards.scalars().all())
    
