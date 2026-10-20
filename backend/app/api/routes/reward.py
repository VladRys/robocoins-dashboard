from fastapi import APIRouter, Depends
from app.models import reward
from app.schemas.reward import RewardResponse
from app.services.reward import RewardService, get_reward_service

rewards_router = APIRouter(prefix="/rewards", tags = ["rewards"])

@rewards_router.get("", response_model=list[RewardResponse])
async def get_all_rewards(self, rewards_service: RewardService = Depends(get_reward_service)) -> list[RewardResponse]:
    rewards = await rewards_service.get_all_rewards()
    return [RewardResponse.model_validate(reward) for reward in rewards]

