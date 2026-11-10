from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.core.enums import UserRole
from app.schemas.base import APIResponse
from app.schemas.reward import RewardResponse

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
    avatar_ring: str | None = None
    balance: float
    hash_access_key: str

    # Access code - keyword for auth.
    access_code: str

    @field_validator("balance")
    @classmethod
    def normalize_balance(cls, balance: float) -> float:
        return round(balance + 1e-9, 1)

class StudentGoalChangeResponse(APIResponse):
    new_goal: RewardResponse

class StudentGoalChangeRequest(BaseModel):
    new_goal_reward_id: int

class StudentProfileResponse(APIResponse):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    role: UserRole = UserRole.STUDENT
    name: str
    course_names: list[str]
    group_ids: list[int]
    avatar: str | None = None
    avatar_ring: str | None = None
    balance: float
    current_goal: str | None = None

    @field_validator("balance")
    @classmethod
    def normalize_balance(cls, balance: float) -> float:
        return round(balance + 1e-9, 1)

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
            "avatar_ring": value.avatar_ring,
            "balance": value.balance,
            "current_goal": getattr(value, "current_goal", None),
        }


class BalanceLeaderboardEntry(BaseModel):
    rank: int
    student_id: int
    name: str
    avatar: str | None = None
    balance: float
    course_names: list[str]

    @field_validator("balance")
    @classmethod
    def normalize_balance(cls, balance: float) -> float:
        return round(balance + 1e-9, 1)


class BalanceLeaderboardResponse(BaseModel):
    entries: list[BalanceLeaderboardEntry]
    total: int
    limit: int
    offset: int


class BalanceLeaderboardRankResponse(BaseModel):
    student_id: int
    rank: int
    balance: float

    @field_validator("balance")
    @classmethod
    def normalize_balance(cls, balance: float) -> float:
        return round(balance + 1e-9, 1)

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
