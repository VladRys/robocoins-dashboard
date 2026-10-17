from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.enums import StatusEnum
from app.core.enums import UserRole


class TeacherRegistrationRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class TeacherGroupProfile(BaseModel):
    id: int
    name: str
    course_id: int
    course_name: str
    students_count: int


class TeacherResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str = StatusEnum.SUCCESS
    code: int = 200
    id: int
    user_id: int
    name: str
    role: UserRole = UserRole.TEACHER


class TeacherProfileResponse(TeacherResponse):
    groups: list[TeacherGroupProfile] = Field(default_factory=list)


class TeacherAssignmentRequest(BaseModel):
    teacher_ids: list[int] = Field(default_factory=list, max_length=2)

    @field_validator("teacher_ids")
    @classmethod
    def teacher_ids_must_be_unique(cls, teacher_ids: list[int]) -> list[int]:
        if len(set(teacher_ids)) != len(teacher_ids):
            raise ValueError("Teacher IDs must be unique")
        return teacher_ids