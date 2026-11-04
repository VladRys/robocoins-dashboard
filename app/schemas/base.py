from pydantic import BaseModel

from app.core.enums import StatusEnum


class APIResponse(BaseModel):
    status: str = StatusEnum.SUCCESS
    code: int = 200
