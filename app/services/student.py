
import uuid

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.access_code import generate_access_code
from app.models.student import Student
from app.models.group import Group
from app.models.user import User
from app.repositories.student import StudentRepository
from app.schemas.student import StudentCreateRequest
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
        return generate_access_code()

    async def generate_unique_access_code(self) -> str:
        """Generate a unique access code."""
        while True:
            new_code = self.generate_access_code()
            existing_user = await self.db.scalar(
                select(User.id).where(User.access_code == new_code)
            )
            if existing_user is None:
                return new_code

    async def create_student(self, student: StudentCreateRequest) -> Student:
        access_code = await self.generate_unique_access_code()
        user = User(
            name=student.name,
            role=UserRole.STUDENT.value,
            access_code=access_code,
        )
        self.db.add(user)
        await self.db.flush()
        groups = list((await self.db.scalars(
            select(Group)
            .options(selectinload(Group.course))
            .where(Group.id.in_(student.group_ids))
        )).all())
        if len(groups) != len(student.group_ids):
            raise ValueError("One or more groups were not found")
        new_student = Student(
            id=user.id,
            user_id=user.id,
            name=student.name,
            avatar=student.avatar,
            balance=0,
            groups=groups,
            hash_access_key=self.generate_hash_access_key(),
            access_code=access_code,
        )
        return await self.repository.create_student(new_student)

    async def get_student_by_id(self, student_id: int) -> Student | None:
        return await self.repository.get_student_by_id(student_id)

    async def get_all_students(self) -> list[Student]:
        return await self.repository.get_all_students()

    async def is_student_in_teacher_group(
        self,
        student_id: int,
        teacher_id: int,
    ) -> bool:
        return await self.repository.is_student_in_teacher_group(student_id, teacher_id)

    async def update_avatar(self, student_id: int, avatar: str) -> Student | None:
        return await self.repository.update_avatar(student_id, avatar)

    async def update_nickname(self, student_id: int, nickname: str) -> Student | None:
        return await self.repository.update_nickname(student_id, nickname)

    async def get_student_by_access_code(self, access_code: str) -> Student | None:
        return await self.repository.get_student_by_access_code(access_code)

    async def update_student_access_code(self, student_id: int) -> Student | None:
        new_access_code = await self.generate_unique_access_code()
        return await self.repository.update_access_code(student_id, new_access_code)

async def get_student_service(db: AsyncSession = Depends(get_db)) -> StudentService:
    repository = StudentRepository(db)
    return StudentService(db, repository)
