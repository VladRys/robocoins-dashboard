from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.core.enums import StatusEnum
from app.core.enums import UserRole

class StudentCreateRequest(BaseModel):
    name: str
    avatar: str
    group_ids: list[int] = Field(min_length=1)

    @field_validator("group_ids")
    @classmethod
    def group_ids_must_be_unique(cls, group_ids: list[int]) -> list[int]:
        if len(group_ids) != len(set(group_ids)):
            raise ValueError("Group IDs must be unique")
        return group_ids

class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: str = StatusEnum.SUCCESS
    code: int = 200
    id: int
    user_id: int
    role: UserRole = UserRole.STUDENT
    name: str
    course_names: list[str]
    group_ids: list[int]
    avatar: str | None = None
    balance: int
    hash_access_key: str

    # Access code - keyword for auth.
    access_code: str

class StudentProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: str = StatusEnum.SUCCESS
    code: int = 200
    id: int
    user_id: int
    role: UserRole = UserRole.STUDENT
    name: str
    course_names: list[str]
    group_ids: list[int]
    avatar: str | None = None
    balance: int

    @model_validator(mode="before")
    @classmethod
    def read_group_ids(cls, value):
        if (
            isinstance(value, dict)
            or hasattr(value, "group_ids")
            or not hasattr(value, "balance")
        ):
            return value
        return {
            "id": value.id,
            "user_id": value.user_id,
            "name": value.name,
            "group_ids": [group.id for group in value.groups],
            "course_names": list(dict.fromkeys(
                group.course.name for group in value.groups
            )),
            "avatar": value.avatar,
            "balance": value.balance,
        }
