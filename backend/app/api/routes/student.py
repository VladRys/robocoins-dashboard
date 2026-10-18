from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_authenticated_teacher, get_authenticated_user
from core.enums import StatusEnum
from app.core.enums import HttpErrorMessage
from models.user import User
from schemas.student import StudentCreateRequest, StudentResponse, StudentProfileResponse
from services.student import StudentService, get_student_service

student_router = APIRouter(
    prefix="/student",
    tags=["students"],
)

@student_router.post("/register", response_model=StudentResponse)
async def create_student(
    student: StudentCreateRequest,
    service: StudentService = Depends(get_student_service),
    _user: User = Depends(get_authenticated_teacher),
) -> StudentResponse:
    try:
        new_student = await service.create_student(student)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

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
