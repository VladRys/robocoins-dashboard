
import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.student import Student
from repositories.student import StudentRepository
from schemas.student import StudentCreateRequest


class StudentService:
    def __init__(self, db: AsyncSession, repository: StudentRepository):
        self.db = db
        self.repository = repository

    @staticmethod
    def generate_hash_access_key() -> str:
        return uuid.uuid4().hex

    async def create_student(self, student: StudentCreateRequest) -> Student:
        new_student = Student(
            name=student.name,
            group=student.group,
            avatar=student.avatar,
            balance=0,
            hash_access_key=self.generate_hash_access_key(),
        )
        return await self.repository.create_student(new_student)


async def get_student_service(db: AsyncSession = Depends(get_db)) -> StudentService:
    repository = StudentRepository(db)
    return StudentService(db, repository)