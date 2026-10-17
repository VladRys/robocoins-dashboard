from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.enums import UserRole


class TeacherRegistrationRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class TeacherResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    role: UserRole = UserRole.TEACHER


class TeacherAssignmentRequest(BaseModel):
    teacher_ids: list[int] = Field(default_factory=list, max_length=2)

    @field_validator("teacher_ids")
    @classmethod
    def teacher_ids_must_be_unique(cls, teacher_ids: list[int]) -> list[int]:
        if len(set(teacher_ids)) != len(teacher_ids):
            raise ValueError("Teacher IDs must be unique")
        return teacher_ids