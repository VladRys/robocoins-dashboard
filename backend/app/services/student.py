
import random
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

    async def _generate_random_id(self) -> int:
        """Generate a random student ID."""
        return random.randint(100000, 999999)

    async def generate_unique_student_id(self) -> int:
        """Generate a unique student ID."""
        while True:
            new_id = await self._generate_random_id()
            existing_student = await self.get_student_by_id(new_id)
            if not existing_student:
                return new_id

    async def create_student(self, student: StudentCreateRequest) -> Student:
        new_student = Student(
            id = await self.generate_unique_student_id(),
            name=student.name,
            group=student.group,
            avatar=student.avatar,
            balance=0,
            hash_access_key=self.generate_hash_access_key(),
        )
        return await self.repository.create_student(new_student)

    async def get_student_by_id(self, student_id: int) -> Student:
        return await self.repository.get_student_by_id(student_id)


async def get_student_service(db: AsyncSession = Depends(get_db)) -> StudentService:
    repository = StudentRepository(db)
    return StudentService(db, repository)