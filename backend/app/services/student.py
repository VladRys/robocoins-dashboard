
from core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends

from models.student import Student
from repositories.student import StudentRepository
from schemas.student import StudentCreateRequest, StudentResponse


class StudentService:
    def __init__(self, db: AsyncSession, repository: StudentRepository):
        self.db = db
        self.repository = repository

    async def create_student(self, student: StudentCreateRequest) -> Student:
        new_student = Student(
            name=student.name,
            group=student.group,
            avatar=student.avatar,
            balance=0,
            hash_access_key="some_generated_hash",
        )
        return await self.repository.create_student(new_student)

async def get_student_service(db: AsyncSession = Depends(get_db)) -> StudentService:
    repository = StudentRepository(db)
    return StudentService(db, repository)