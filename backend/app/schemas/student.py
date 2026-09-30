from pydantic import BaseModel, ConfigDict
from core.enums import StatusEnum

class StudentCreateRequest(BaseModel):
    name: str
    group: str
    avatar: str | None = None


class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: str = StatusEnum.SUCCESS
    code: int = 200
    id: int
    name: str
    group: str
    avatar: str | None = None
    balance: int
    hash_access_key: str