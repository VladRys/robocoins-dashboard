from fastapi import APIRouter, Depends, HTTPException, Response

from app.api.dependencies import get_achievement_service, get_authenticated_admin
from app.core.enums import AchievementCategory
from app.models.achievement import Achievement
from app.models.user import User
from app.schemas.achievement import AchievementCreateRequest, AchievementResponse
from app.services.achievement import AchievementService


achievement_router = APIRouter(prefix="/achievements", tags=["achievements"])


@achievement_router.get("", response_model=list[AchievementResponse])
async def get_achievements(
    service: AchievementService = Depends(get_achievement_service),
    _user: User = Depends(get_authenticated_admin),
) -> list[AchievementResponse]:
    achievements = await service.get_coin_earning_achievements()
    return [AchievementResponse.model_validate(item) for item in achievements]


@achievement_router.post(
    "",
    response_model=AchievementResponse,
    status_code=201,
)
async def create_coin_earning_achievement(
    request: AchievementCreateRequest,
    service: AchievementService = Depends(get_achievement_service),
    _user: User = Depends(get_authenticated_admin),
) -> AchievementResponse:
    achievement = await service.create_achievement(
        Achievement(
            name=request.name,
            description=request.description,
            icon=request.icon,
            type=request.type,
            category=AchievementCategory.COINS_EARNING.value,
            required_coins=request.required_coins,
        )
    )
    return AchievementResponse.model_validate(achievement)


@achievement_router.delete("/{achievement_id}", status_code=204)
async def delete_coin_earning_achievement(
    achievement_id: int,
    service: AchievementService = Depends(get_achievement_service),
    _user: User = Depends(get_authenticated_admin),
) -> Response:
    achievement = await service.get_achievement_by_id(achievement_id)
    if achievement is None or achievement.category != AchievementCategory.COINS_EARNING:
        raise HTTPException(status_code=404, detail="Achievement not found")
    await service.delete_achievement(achievement_id)
    return Response(status_code=204)
