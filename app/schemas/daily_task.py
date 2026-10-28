from datetime import date, datetime

from pydantic import BaseModel, Field

from app.core.enums import TaskType

class DailyTaskResponse(BaseModel):
    id: int
    date: date
    type: TaskType
    question: str
    options: list[str] | None = None
    image_url: str | None = None
    hotspots: list[dict[str, int | str]] | None = None
    completed_at: datetime | None = None
    reward: float


class DailyTaskAnswer(BaseModel):
    answer: str = Field(min_length=1, max_length=200, strict=True)


class DailyTaskAnswerResponse(BaseModel):
    correct: bool
    completed_at: datetime
    reward: float
    balance: float
