import asyncio
from unittest.mock import AsyncMock

import pytest

from app.core.enums import RewardType
from app.models.reward import Reward
from app.services.reward import RewardService


def create_reward(reward_id: int, name: str, price: int) -> Reward:
    return Reward(
        id=reward_id,
        name=name,
        price=price,
        description=None,
        type=RewardType.REWARD,
        course_category=None,
    )


def test_student_reward_progress_uses_saved_goal_id():
    async def run():
        goal = create_reward(1, "Python course", 100)
        repository = AsyncMock()
        repository.get_reward_by_id.return_value = goal
        service = RewardService(repository)

        progress = await service.get_student_reward_progress(
            student_id=123,
            balance=40.0,
            current_goal="Python course",
            current_goal_reward_id=1,
        )

        assert progress.current_goal is goal
        assert progress.coins_remaining == 60.0
        assert progress.progress_percent == 40.0
        repository.get_reward_by_id.assert_awaited_once_with(1)
        repository.get_rewards_by_name.assert_not_awaited()
        repository.get_rewards_for_student.assert_not_awaited()

    asyncio.run(run())


@pytest.mark.parametrize("current_goal", [None, "Removed reward"])
def test_student_reward_progress_falls_back_to_nearest_reward_above_balance(
    current_goal,
):
    async def run():
        nearest = create_reward(2, "Nearest reward", 75)
        repository = AsyncMock()
        repository.get_rewards_by_name.return_value = []
        repository.get_rewards_for_student.return_value = [
            create_reward(3, "More expensive", 150),
            nearest,
            create_reward(4, "Already affordable", 20),
        ]
        service = RewardService(repository)

        progress = await service.get_student_reward_progress(
            student_id=123,
            balance=40.0,
            current_goal=current_goal,
        )

        assert progress.current_goal is nearest
        assert progress.coins_remaining == 35.0
        assert progress.progress_percent == 53.33
        repository.get_rewards_for_student.assert_awaited_once_with(123)
        if current_goal is None:
            repository.get_rewards_by_name.assert_not_awaited()
        else:
            repository.get_rewards_by_name.assert_awaited_once_with(current_goal)

    asyncio.run(run())


def test_student_reward_progress_does_not_guess_ambiguous_legacy_goal():
    async def run():
        nearest = create_reward(4, "Nearest reward", 75)
        repository = AsyncMock()
        repository.get_rewards_by_name.return_value = [
            create_reward(1, "Steam game", 70),
            create_reward(2, "Steam game", 70),
        ]
        repository.get_rewards_for_student.return_value = [nearest]
        service = RewardService(repository)

        progress = await service.get_student_reward_progress(
            student_id=123,
            balance=40.0,
            current_goal="Steam game",
        )

        assert progress.current_goal is nearest
        repository.get_rewards_by_name.assert_awaited_once_with("Steam game")
        repository.get_rewards_for_student.assert_awaited_once_with(123)

    asyncio.run(run())


def test_student_reward_progress_is_empty_when_no_reward_is_above_balance():
    async def run():
        repository = AsyncMock()
        repository.get_rewards_for_student.return_value = [
            create_reward(1, "Already affordable", 20),
        ]
        service = RewardService(repository)

        progress = await service.get_student_reward_progress(
            student_id=123,
            balance=40.0,
            current_goal=None,
        )

        assert progress.current_goal is None
        assert progress.coins_remaining is None
        assert progress.progress_percent is None

    asyncio.run(run())
