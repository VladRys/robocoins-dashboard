from core.enums import StatusEnum
from pydantic import BaseModel, ConfigDict, Field
from .group import GroupResponse

class CourseCreateRequest(BaseModel):
    name: str = Field(..., description="Name of the course")


class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str = StatusEnum.SUCCESS
    code: int = 200
    id: int
    name: str
    groups: list[GroupResponse] = Field(default_factory=list, description="Groups associated with the course")
    groups_count: int = 0