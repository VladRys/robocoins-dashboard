from app.core.enums import StatusEnum
from pydantic import BaseModel, ConfigDict, Field
from app.core.enums import CourseCategory
from .group import CourseGroupResponse

class CourseCreateRequest(BaseModel):
    name: str = Field(..., description="Name of the course")
    category: CourseCategory = CourseCategory.EMBEDDED

class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str = StatusEnum.SUCCESS
    code: int = 200
    id: int
    name: str
    category: CourseCategory
    groups: list[CourseGroupResponse] = Field(default_factory=list, description="Groups associated with the course")
    groups_count: int = 0
