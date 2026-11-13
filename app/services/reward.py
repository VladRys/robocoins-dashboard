from dataclasses import dataclass

from app.models.reward import Reward
from app.core.enums import CourseCategory
from app.repositories.reward import RewardRepository


@dataclass(frozen=True)
class StudentRewardProgress:
    current_goal: Reward | None
    coins_remaining: float | None
    progress_percent: float | None


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

    async def get_rewards_by_name(self, reward_name: str) -> list[Reward]:
        return await self.repository.get_rewards_by_name(reward_name)

    async def get_all_rewards(self, course_category: CourseCategory | None = None) -> list[Reward]:
        return await self.repository.get_all_rewards(course_category)

    async def get_rewards_for_student(self, student_id: int) -> list[Reward]:
        return await self.repository.get_rewards_for_student(student_id)

    async def get_student_reward_progress(
        self,
        *,
        student_id: int,
        balance: float,
        current_goal: str | None,
        current_goal_reward_id: int | None = None,
    ) -> StudentRewardProgress:
        goal_reward = None
        if current_goal_reward_id is not None:
            goal_reward = await self.get_reward_by_id(current_goal_reward_id)
        elif current_goal is not None:
            matching_rewards = await self.get_rewards_by_name(current_goal)
            if len(matching_rewards) == 1:
                goal_reward = matching_rewards[0]

        if goal_reward is None:
            available_rewards = await self.get_rewards_for_student(student_id)
            goal_reward = min(
                (reward for reward in available_rewards if reward.price > balance),
                key=lambda reward: reward.price,
                default=None,
            )

        if goal_reward is None:
            return StudentRewardProgress(
                current_goal=None,
                coins_remaining=None,
                progress_percent=None,
            )

        return StudentRewardProgress(
            current_goal=goal_reward,
            coins_remaining=max(0.0, round(goal_reward.price - balance, 1)),
            progress_percent=(
                100.0
                if goal_reward.price <= 0
                else round(min(balance / goal_reward.price * 100, 100), 2)
            ),
        )

