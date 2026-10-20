from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import await_

from app.models import reward
from models.reward import Reward

class RewardRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

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
