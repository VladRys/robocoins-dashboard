from pydantic import BaseModel, ConfigDict


class StudentCreateRequest(BaseModel):
    name: str
    group: str
    avatar: str | None = None


class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    group: str
    avatar: str | None = None
    balance: int
    hash_access_key: str