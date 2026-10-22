from pydantic import BaseModel, ConfigDict, model_validator

from app.core.enums import RewardType, StatusEnum

class RewardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: int
    description: str | None
    type: RewardType
    course_id: int | None

class CreateRewardRequest(BaseModel):
    name: str
    price: int
    description: str | None = None
    type: RewardType
    course_id: int | None = None

    @model_validator(mode="after")
    def validate_type_course(self):
        if self.type == RewardType.PRIVILEGE and self.course_id is not None:
            raise ValueError("Privileges are available for all courses and cannot be assigned to one course")
        if self.type == RewardType.REWARD and self.course_id is None:
            raise ValueError("A reward must be assigned to a course")
        return self

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
