from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_authenticated_user, get_user_service
from app.core.enums import HttpErrorMessage
from app.schemas.user import UserResponse
from app.services.users import UserService


users_router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@users_router.get("", response_model=list[UserResponse])
async def get_users(
    service: UserService = Depends(get_user_service),
    _user = Depends(get_authenticated_user),
) -> list[UserResponse]:
    users = await service.get_users()
    return [UserResponse.model_validate(user) for user in users]


@users_router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    service: UserService = Depends(get_user_service),
    _user = Depends(get_authenticated_user),
) -> UserResponse:
    user = await service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=HttpErrorMessage.USER_NOT_FOUND)
    return UserResponse.model_validate(user)
