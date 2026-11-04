from pydantic import BaseModel, ConfigDict, Field
from app.core.enums import CourseCategory
from app.schemas.base import APIResponse
from .group import CourseGroupResponse

class CourseCreateRequest(BaseModel):
    name: str = Field(..., description="Name of the course")
    category: CourseCategory = CourseCategory.EMBEDDED

class CourseResponse(APIResponse):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: CourseCategory
    groups: list[CourseGroupResponse] = Field(default_factory=list, description="Groups associated with the course")
    groups_count: int = 0
