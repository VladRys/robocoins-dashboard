from pydantic import BaseModel

from app.core.enums import StatusEnum

class RewardResponse(BaseModel):
    id: int
    name: str
    price: int

    code: int = 200
    status: str = StatusEnum.SUCCESS

class CreateRewardRequest(BaseModel):
    name: str
    price: int
