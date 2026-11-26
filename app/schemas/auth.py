from pydantic import BaseModel, Field

from app.core.enums import UserRole
from app.schemas.base import APIResponse


class UserLoginRequest(BaseModel):
    code: str = Field(min_length=1, max_length=128)


class LoginUser(BaseModel):
    id: int
    user_id: int
    name: str
    role: UserRole


class UserLoginResponse(APIResponse):
    message: str
    session_token: str
    user: LoginUser


class GoogleAuthorizationResponse(BaseModel):
    authorization_url: str


class GoogleLinkStatusResponse(BaseModel):
    linked: bool
    email: str | None = None


class GoogleOAuthUserResponse(BaseModel):
    id: int
    user_id: int
    name: str
    role: UserRole


class GoogleOAuthCallbackResponse(BaseModel):
    status: str
    user: GoogleOAuthUserResponse | None = None


class AdminProfileResponse(BaseModel):
    id: int
    user_id: int
    name: str
    role: UserRole = UserRole.ADMIN


class UserLogoutResponse(APIResponse):
    message: str


class StudentCredentialsResponse(APIResponse):
    user_id: int
    name: str
    access_code: str
