from pydantic import BaseModel, ConfigDict

from app.core.enums import StatusEnum

class RewardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: int
    description: str | None

class CreateRewardRequest(BaseModel):
    name: str
    price: int
    description: str | None = None

class RewardCreationResponse(BaseModel):
    reward: RewardResponse
    code: int = 200
    status: str = StatusEnum.SUCCESS

class RewardProgressResponse(BaseModel):
    balance: int
    reward: RewardResponse | None
    coins_remaining: int | None
    progress_percent: float | None
    code: int = 200
    status: str = StatusEnum.SUCCESS
