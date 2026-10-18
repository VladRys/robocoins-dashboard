from fastapi import APIRouter, Depends, HTTPException

from schemas.user import UserResponse
from services.users import UserService, get_user_service


users_router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@users_router.get("", response_model=list[UserResponse])
async def get_users(
    service: UserService = Depends(get_user_service),
) -> list[UserResponse]:
    users = await service.get_users()
    return [UserResponse.model_validate(user) for user in users]


@users_router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    user = await service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)
