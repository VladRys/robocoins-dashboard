from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class StreakResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    start_date: datetime
    end_date: datetime | None
    days: int

class StreakRequest(BaseModel):
    student_id: int


class StreakDaysUpdate(BaseModel):
    days: int = Field(ge=0)

class LongestStreakResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    days: int

