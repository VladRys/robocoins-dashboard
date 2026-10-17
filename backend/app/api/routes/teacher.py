from fastapi import APIRouter, Depends, HTTPException

from schemas.teacher import (
    TeacherGroupProfile,
    TeacherProfileResponse,
    TeacherRegistrationRequest,
    TeacherResponse,
)
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
    return TeacherResponse(
        id=teacher.id,
        user_id=teacher.id,
        name=teacher.name,
        role=teacher.role,
    )


@teacher_router.get("/{teacher_id}", response_model=TeacherProfileResponse)
async def get_teacher_profile(
    teacher_id: int,
    service: UserService = Depends(get_user_service),
) -> TeacherProfileResponse:
    profile = await service.get_teacher_profile(teacher_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Teacher not found")

    teacher, groups = profile
    return TeacherProfileResponse(
        id=teacher.id,
        user_id=teacher.id,
        name=teacher.name,
        role=teacher.role,
        groups=[
            TeacherGroupProfile(
                id=group.id,
                name=group.name,
                course_id=group.course_id,
                course_name=group.course.name,
                students_count=len(group.students),
            )
            for group in groups
        ],
    )
