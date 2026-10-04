from pydantic import BaseModel, ConfigDict
from core.enums import StatusEnum

class StudentCreateRequest(BaseModel):
    name: str
    avatar: str
    course: str

class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: str = StatusEnum.SUCCESS
    code: int = 200
    id: int
    name: str
    course: str
    group_id: str | None = None
    avatar: str | None = None
    balance: int
    hash_access_key: str

    # Access code - keyword for auth.
    access_code: str
