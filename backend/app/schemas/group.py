from core.enums import StatusEnum
from pydantic import BaseModel, ConfigDict, Field

class GroupCreateRequest(BaseModel):
    name: str = Field(..., description="Name of the group")
    course_id: int = Field(..., description="ID of the associated course")


class GroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str = StatusEnum.SUCCESS
    code: int = 200
    id: int
    name: str
    course_id: int
    students: list[int] = Field(default_factory=list, description="List of student IDs in the group")
    students_count: int = 0