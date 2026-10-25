from app.core.enums import StatusEnum
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.schemas.student import StudentProfileResponse

class GroupCreateRequest(BaseModel):
    name: str = Field(..., description="Name of the group")
    course_id: int = Field(..., description="ID of the associated course")
    teacher_ids: list[int] = Field(
        default_factory=list,
        max_length=2,
        description="One or two teacher user IDs",
    )

    @field_validator("teacher_ids")
    @classmethod
    def teacher_ids_must_be_unique(cls, teacher_ids: list[int]) -> list[int]:
        if len(set(teacher_ids)) != len(teacher_ids):
            raise ValueError("Teacher IDs must be unique")
        return teacher_ids


class GroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str = StatusEnum.SUCCESS
    code: int = 200
    id: int
    name: str
    course_id: int
    students: list[StudentProfileResponse] = Field(
        default_factory=list,
        description="Students in the group",
    )
    students_count: int = 0
    teacher_ids: list[int] = Field(
        default_factory=list,
        description="User IDs of the group's teachers",
    )
    
class CourseGroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str = StatusEnum.SUCCESS
    code: int = 200
    id: int
    name: str
    course_id: int
    students_count: int = 0
    teacher_ids: list[int] = Field(
        default_factory=list,
        description="User IDs of the group's teachers",
    )