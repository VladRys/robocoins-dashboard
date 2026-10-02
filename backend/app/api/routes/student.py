from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.enums import StatusEnum
from core.database import get_db
from schemas.student import StudentCreateRequest, StudentResponse
from services.student import StudentService, get_student_service

student_router = APIRouter(
    prefix="/student",
    tags=["students"],
)

@student_router.post("/register", response_model=StudentResponse)
async def create_student(
    student: StudentCreateRequest,
    db: AsyncSession = Depends(get_db),
    service: StudentService = Depends(get_student_service),
) -> StudentResponse:
    new_student = await service.create_student(student)

    if new_student is None:
        raise HTTPException(status_code=500, detail="Failed to create student")

    return StudentResponse(
        id=new_student.id,
        name=new_student.name,
        group=new_student.group,
        avatar=new_student.avatar,
        balance=new_student.balance,
        hash_access_key=new_student.hash_access_key,
        status=StatusEnum.SUCCESS,
        code=200
    )


@student_router.get("/{student_id}", response_model=StudentResponse)
async def get_student_by_id(
    student_id: int,
    service: StudentService = Depends(get_student_service),
) -> StudentResponse:
    student = await service.get_student_by_id(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    return StudentResponse.model_validate(student)
