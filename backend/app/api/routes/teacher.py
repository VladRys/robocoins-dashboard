from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_authenticated_admin, get_authenticated_teacher, get_authenticated_user
from app.core.enums import HttpErrorMessage
from app.models.user import User
from app.schemas.group import CourseGroupResponse
from app.schemas.teacher import (
    TeacherGroupProfile,
    TeacherProfileResponse,
    TeacherRegistrationRequest,
    TeacherRegistrationResponse,
)
from app.services.group import GroupService, get_group_service
from app.services.users import UserService, get_user_service


teacher_router = APIRouter(
    prefix="/teacher",
    tags=["teachers"],
)

@teacher_router.get(
    "/course/{course_id}/groups",
    response_model=list[CourseGroupResponse],
)
async def get_teacher_groups_by_course(
    course_id: int,
    teacher: User = Depends(get_authenticated_teacher),
    service: GroupService = Depends(get_group_service),
) -> list[CourseGroupResponse]:
    groups = await service.get_groups_by_teacher_and_course(teacher.id, course_id)
    return [
        CourseGroupResponse(
            id=group.id,
            name=group.name,
            course_id=group.course_id,
            students_count=len(group.students),
            teacher_ids=[
                teacher_id
                for teacher_id in (group.teacher_1_id, group.teacher_2_id)
                if teacher_id is not None
            ],
        )
        for group in groups
    ]


@teacher_router.get(
    "/groups",
    response_model=list[CourseGroupResponse],
)
async def get_teacher_groups(
    teacher: User = Depends(get_authenticated_teacher),
    service: GroupService = Depends(get_group_service),
) -> list[CourseGroupResponse]:
    groups = await service.get_groups_by_teacher(teacher.id)
    return [
        CourseGroupResponse(
            id=group.id,
            name=group.name,
            course_id=group.course_id,
            students_count=len(group.students),
            teacher_ids=[
                teacher_id
                for teacher_id in (group.teacher_1_id, group.teacher_2_id)
                if teacher_id is not None
            ],
        )
        for group in groups
    ]


@teacher_router.post("/register", response_model=TeacherRegistrationResponse)
async def register_teacher(
    request: TeacherRegistrationRequest,
    service: UserService = Depends(get_user_service),
    _admin: User = Depends(get_authenticated_admin),
) -> TeacherRegistrationResponse:
    teacher = await service.register_teacher(request.name)
    if teacher is None:
        raise HTTPException(status_code=500, detail=HttpErrorMessage.FAILED_TO_CREATE_TEACHER)
    return TeacherRegistrationResponse(
        id=teacher.id,
        user_id=teacher.id,
        name=teacher.name,
        role=teacher.role,
        access_code=teacher.access_code,
    )


@teacher_router.get("/{teacher_id}", response_model=TeacherProfileResponse)
async def get_teacher_profile(
    teacher_id: int,
    service: UserService = Depends(get_user_service),
    _user = Depends(get_authenticated_user),
) -> TeacherProfileResponse:
    profile = await service.get_teacher_profile(teacher_id)
    if profile is None:
        raise HTTPException(status_code=404, detail=HttpErrorMessage.TEACHER_NOT_FOUND)

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
