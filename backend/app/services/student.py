
import random
import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from models.student import Student
from models.user import User
from repositories.student import StudentRepository
from schemas.student import StudentCreateRequest
from app.core.enums import UserRole


class StudentService:
    def __init__(self, db: AsyncSession, repository: StudentRepository):
        self.db = db
        self.repository = repository

    @staticmethod
    def generate_hash_access_key() -> str:
        return uuid.uuid4().hex

    @staticmethod
    def generate_access_code() -> str:
        """Generate a random access code. (symbols + digits)"""
        characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        return "".join(random.choice(characters) for _ in range(8))

    async def generate_unique_access_code(self) -> str:
        """Generate a unique access code."""
        while True:
            new_code = self.generate_access_code()
            existing_student = await self.get_student_by_access_code(new_code)
            if not existing_student:
                return new_code

    async def create_student(self, student: StudentCreateRequest) -> Student:
        user = User(name=student.name, role=UserRole.STUDENT.value)
        self.db.add(user)
        await self.db.flush()
        new_student = Student(
            id=user.id,
            user_id=user.id,
            name=student.name,
            avatar=student.avatar,
            balance=0,
            course_name=student.course_name,
            group_id=student.group_id,
            hash_access_key=self.generate_hash_access_key(),
            access_code=await self.generate_unique_access_code(),
        )
        return await self.repository.create_student(new_student)

    async def get_student_by_id(self, student_id: int) -> Student | None:
        return await self.repository.get_student_by_id(student_id)

    async def get_student_by_access_code(self, access_code: str) -> Student | None:
        return await self.repository.get_student_by_access_code(access_code)

async def get_student_service(db: AsyncSession = Depends(get_db)) -> StudentService:
    repository = StudentRepository(db)
    return StudentService(db, repository)
