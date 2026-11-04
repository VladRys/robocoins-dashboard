from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.core.enums import UserRole
from app.schemas.base import APIResponse

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

class StudentResponse(APIResponse):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    role: UserRole = UserRole.STUDENT
    name: str
    course_names: list[str]
    group_ids: list[int]
    avatar: str | None = None
    balance: float
    hash_access_key: str

    # Access code - keyword for auth.
    access_code: str

class StudentProfileResponse(APIResponse):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    role: UserRole = UserRole.STUDENT
    name: str
    course_names: list[str]
    group_ids: list[int]
    avatar: str | None = None
    balance: float

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


class BalanceLeaderboardEntry(BaseModel):
    rank: int
    student_id: int
    name: str
    avatar: str | None = None
    balance: float
    course_names: list[str]


class BalanceLeaderboardResponse(BaseModel):
    entries: list[BalanceLeaderboardEntry]
    total: int
    limit: int
    offset: int


class BalanceLeaderboardRankResponse(BaseModel):
    student_id: int
    rank: int
    balance: float

class StudentAvatarEditRequest(BaseModel):
    new_avatar: str = Field(min_length=1, max_length=16)

    @field_validator("new_avatar")
    @classmethod
    def avatar_must_not_be_blank(cls, avatar: str) -> str:
        avatar = avatar.strip()
        if not avatar:
            raise ValueError("Avatar must not be blank")
        return avatar


class StudentNicknameEditRequest(BaseModel):
    new_nickname: str = Field(min_length=1, max_length=200)

    @field_validator("new_nickname")
    @classmethod
    def nickname_must_not_be_blank(cls, nickname: str) -> str:
        nickname = nickname.strip()
        if not nickname:
            raise ValueError("Nickname must not be blank")
        return nickname
