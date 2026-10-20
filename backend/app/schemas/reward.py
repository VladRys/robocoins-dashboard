from pydantic import BaseModel

from app.core.enums import StatusEnum

class RewardResponse(BaseModel):
    id: int
    name: str
    price: int

class CreateRewardRequest(BaseModel):
    name: str
    price: int

class RewardCreationResponse(BaseModel):
    reward: RewardResponse
    code: int = 200
    status: str = StatusEnum.SUCCESS