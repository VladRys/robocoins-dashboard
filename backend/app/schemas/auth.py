from pydantic import BaseModel, Field

from app.core.enums import UserRole
from app.core.enums import StatusEnum


class UserLoginRequest(BaseModel):
    code: str


class AdminLoginRequest(BaseModel):
    password: str = Field(min_length=1, max_length=1024)


class LoginUser(BaseModel):
    id: int
    user_id: int
    name: str
    role: UserRole


class UserLoginResponse(BaseModel):
    message: str
    session_token: str
    user: LoginUser
    status: str = StatusEnum.SUCCESS
    code: int = 200


class AdminProfileResponse(BaseModel):
    id: int
    user_id: int
    name: str
    role: UserRole = UserRole.ADMIN


class UserLogoutResponse(BaseModel):
    message: str
    status: str = StatusEnum.SUCCESS
    code: int = 200


class StudentCredentialsResponse(BaseModel):
    user_id: int
    name: str
    access_code: str
    status: str = StatusEnum.SUCCESS
    code: int = 200
