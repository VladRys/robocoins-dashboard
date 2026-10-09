from pydantic import BaseModel

from core.enums import StatusEnum
class StudentLogin(BaseModel):
    # mb that good idea to left here name instead of access_code only :/
    code: str


class StudentLoginResponse(BaseModel):
    message: str
    session_token: str
    status: str = StatusEnum.SUCCESS
    code: int = 200

class StudentLogoutResponse(BaseModel):
    message: str
    status: str = StatusEnum.SUCCESS
    code: int = 200