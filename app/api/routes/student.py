from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import (
    get_authenticated_admin,
    get_authenticated_user,
    get_authorization_service,
)
from app.api.errors import validation_error_message
from app.core.enums import AuthorizationAction, HttpErrorMessage, StatusEnum
from app.models.user import User
from app.schemas.student import (
    StudentAvatarEditRequest,
    StudentCreateRequest,
    StudentNicknameEditRequest,
    StudentProfileResponse,
    StudentResponse,
)
from app.services.authorization import AuthorizationService
from app.services.student import StudentService, get_student_service

student_router = APIRouter(
    prefix="/student",
    tags=["students"],
)


@student_router.get("", response_model=list[StudentProfileResponse])
async def get_all_students(
    service: StudentService = Depends(get_student_service),
    _admin: User = Depends(get_authenticated_admin),
) -> list[StudentProfileResponse]:
    students = await service.get_all_students()
    return [StudentProfileResponse.model_validate(student) for student in students]


@student_router.post("/register", response_model=StudentResponse)
async def create_student(
    student: StudentCreateRequest,
    service: StudentService = Depends(get_student_service),
) -> StudentResponse:
    try:
        new_student = await service.create_student(student)
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=validation_error_message(
                error,
                HttpErrorMessage.GROUPS_NOT_FOUND,
            ),
        ) from error

    if new_student is None:
        raise HTTPException(status_code=500, detail=HttpErrorMessage.FAILED_TO_CREATE_STUDENT)

    return StudentResponse(
        id=new_student.id,
        user_id=new_student.user_id,
        name=new_student.name,
        group_ids=[group.id for group in new_student.groups],
        course_names=list(dict.fromkeys(group.course.name for group in new_student.groups)),
        avatar=new_student.avatar,
        balance=new_student.balance,
        hash_access_key=new_student.hash_access_key,
        access_code=new_student.access_code,
        status=StatusEnum.SUCCESS,
        code=200,
    )


@student_router.get("/{student_id}", response_model=StudentProfileResponse)
async def get_student_by_id(
    student_id: int,
    service: StudentService = Depends(get_student_service),
    _user: User = Depends(get_authenticated_user),
) -> StudentProfileResponse:
    student = await service.get_student_by_id(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=HttpErrorMessage.STUDENT_NOT_FOUND)

    return StudentProfileResponse.model_validate(student)

@student_router.patch("/{student_id}/avatar", response_model=StudentProfileResponse)
async def edit_student_avatar(
    student_id: int,
    request: StudentAvatarEditRequest,
    service: StudentService = Depends(get_student_service),
    user: User = Depends(get_authenticated_user),
    authorization: AuthorizationService = Depends(get_authorization_service),
) -> StudentProfileResponse:
    student = await service.get_student_by_id(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=HttpErrorMessage.STUDENT_NOT_FOUND)

    can_edit_avatar = await authorization.is_allowed(
        AuthorizationAction.EDIT_STUDENT_AVATAR, user, student_id
    )
    if not can_edit_avatar:
        raise HTTPException(status_code=403, detail="You cannot change this student's avatar")

    updated_student = await service.update_avatar(student_id, request.new_avatar)
    if updated_student is None:
        raise HTTPException(status_code=404, detail=HttpErrorMessage.STUDENT_NOT_FOUND)
    return StudentProfileResponse.model_validate(updated_student)


@student_router.patch("/{student_id}/nickname", response_model=StudentProfileResponse)
async def edit_student_nickname(
    student_id: int,
    request: StudentNicknameEditRequest,
    service: StudentService = Depends(get_student_service),
    user: User = Depends(get_authenticated_user),
    authorization: AuthorizationService = Depends(get_authorization_service),
) -> StudentProfileResponse:
    student = await service.get_student_by_id(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=HttpErrorMessage.STUDENT_NOT_FOUND)

    can_edit_nickname = await authorization.is_allowed(
        AuthorizationAction.EDIT_STUDENT_NICKNAME,
        user,
        student_id,
    )
    if not can_edit_nickname:
        raise HTTPException(status_code=403, detail="You cannot change this student's nickname")

    updated_student = await service.update_nickname(student_id, request.new_nickname)
    if updated_student is None:
        raise HTTPException(status_code=404, detail=HttpErrorMessage.STUDENT_NOT_FOUND)
    return StudentProfileResponse.model_validate(updated_student)
