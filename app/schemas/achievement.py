from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import AchievementType


class AchievementCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=1000)
    icon: str = Field(min_length=1, max_length=32)
    type: AchievementType = AchievementType.BADGE
    required_coins: int = Field(gt=0)


class AchievementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    icon: str
    type: AchievementType
    category: str
    required_coins: int | None


class CoinAchievementProgressItem(AchievementResponse):
    earned: bool
    progress_percent: float


class StudentAchievementProgressResponse(BaseModel):
    earned_coins: float
    achievements: list[CoinAchievementProgressItem]
