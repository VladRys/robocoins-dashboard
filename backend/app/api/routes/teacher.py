from fastapi import APIRouter, Depends, HTTPException

from schemas.teacher import TeacherRegistrationRequest, TeacherResponse
from services.users import UserService, get_user_service


teacher_router = APIRouter(
    prefix="/teacher",
    tags=["teachers"],
)


@teacher_router.post("/register", response_model=TeacherResponse)
async def register_teacher(
    request: TeacherRegistrationRequest,
    service: UserService = Depends(get_user_service),
) -> TeacherResponse:
    teacher = await service.register_teacher(request.name)
    if teacher is None:
        raise HTTPException(status_code=500, detail="Failed to create teacher")
    return TeacherResponse.model_validate(teacher)
