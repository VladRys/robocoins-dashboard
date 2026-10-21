from fastapi import APIRouter, Depends, HTTPException
from app.models.reward import Reward
from app.schemas.reward import RewardResponse, CreateRewardRequest, RewardCreationResponse
from app.services.reward import RewardService, get_reward_service
from app.models.user import User
from api.dependencies import get_authenticated_user
from core.enums import HttpErrorMessage

rewards_router = APIRouter(prefix="/rewards", tags = ["rewards"])
shop_router = APIRouter(prefix="/shop", tags=["shop"])


@shop_router.get("", response_model=list[RewardResponse])
async def get_shop_rewards(
    rewards_service: RewardService = Depends(get_reward_service),
    _user: User = Depends(get_authenticated_user),
) -> list[RewardResponse]:
    rewards = await rewards_service.get_all_rewards()
    return [RewardResponse.model_validate(reward) for reward in rewards]


@shop_router.get("/{reward_id}", response_model=RewardResponse)
async def get_shop_reward(
    reward_id: int,
    rewards_service: RewardService = Depends(get_reward_service),
    _user: User = Depends(get_authenticated_user),
) -> RewardResponse:
    reward = await rewards_service.get_reward_by_id(reward_id)
    if reward is None:
        raise HTTPException(status_code=404, detail="Reward not found")
    return RewardResponse.model_validate(reward)

@rewards_router.get("", response_model=list[RewardResponse])
async def get_all_rewards(self, rewards_service: RewardService = Depends(get_reward_service)) -> list[RewardResponse]:
    rewards = await rewards_service.get_all_rewards()
    return [RewardResponse.model_validate(reward) for reward in rewards]

@rewards_router.post("", response_model = RewardCreationResponse)
async def create_reward(self, request: CreateRewardRequest, rewards_service: RewardService = Depends(get_reward_service), _user: User = Depends(get_authenticated_user)):
    new_reward = await rewards_service.create_reward(reward=Reward(name=request.name, price = request.price, description = request.description))
    if new_reward is None:
        raise HTTPException(status_code = 500, detail=HttpErrorMessage.FAILED_TO_CREATE_REWARD)
    
    return RewardCreationResponse(
        reward = RewardResponse.model_validate(new_reward)
    )
