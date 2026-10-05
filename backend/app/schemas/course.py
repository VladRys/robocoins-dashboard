from pydantic import BaseModel, Field
from core.enums import StatusEnum

class CourseCreateRequest(BaseModel):
    name: str = Field(..., description="Name of the course")
    
class CourseResponse(BaseModel):
    status: str = StatusEnum.SUCCESS
    code: int = 200
    id: int
    name: str
    groups: list[int] = Field(default_factory=list, description="List of group IDs associated with the course")
    groups_count: int = len(groups)