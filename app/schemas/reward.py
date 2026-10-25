from pydantic import BaseModel, ConfigDict, model_validator

from app.core.enums import CourseCategory, RewardType
from app.schemas.base import APIResponse

class RewardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: int
    description: str | None
    type: RewardType
    course_category: CourseCategory | None

class CreateRewardRequest(BaseModel):
    name: str
    price: int
    description: str | None = None
    type: RewardType
    course_category: CourseCategory | None = None

    @model_validator(mode="after")
    def validate_type_course(self):
        if self.type == RewardType.PRIVILEGE and self.course_category is not None:
            raise ValueError("Privileges are available for all courses and cannot be assigned to one category")
        return self

class RewardCreationResponse(APIResponse):
    reward: RewardResponse


class RewardProgressResponse(APIResponse):
    balance: int
    reward: RewardResponse | None
    coins_remaining: int | None
    progress_percent: float | None
