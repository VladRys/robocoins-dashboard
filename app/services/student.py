
import uuid

from app.core.access_code import generate_access_code
from app.models.student import Student
from app.repositories.student import StudentRepository
from app.schemas.student import StudentCreateRequest


class StudentService:
    def __init__(self, repository: StudentRepository):
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
            if not await self.repository.has_access_code(new_code):
                return new_code

    async def create_student(self, student: StudentCreateRequest) -> Student:
        access_code = await self.generate_unique_access_code()
        return await self.repository.create_student(
            name=student.name,
            avatar=student.avatar,
            group_ids=student.group_ids,
            access_code=access_code,
            hash_access_key=self.generate_hash_access_key(),
        )

    async def get_student_by_id(self, student_id: int) -> Student | None:
        return await self.repository.get_student_by_id(student_id)

    async def get_all_students(self) -> list[Student]:
        return await self.repository.get_all_students()

    async def get_balance_leaderboard(
        self, limit: int, offset: int
    ) -> tuple[list[Student], int]:
        return await self.repository.get_balance_leaderboard(limit, offset)

    async def get_balance_leaderboard_rank(
        self, student_id: int
    ) -> tuple[int, Student] | None:
        return await self.repository.get_balance_leaderboard_rank(student_id)

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

    async def change_student_goal(self, student_id: int, goal: str) -> Student | None:
        return await self.repository.change_student_goal(student_id, goal)

    async def get_student_by_access_code(self, access_code: str) -> Student | None:
        return await self.repository.get_student_by_access_code(access_code)

    async def update_student_access_code(self, student_id: int) -> Student | None:
        new_access_code = await self.generate_unique_access_code()
        return await self.repository.update_access_code(student_id, new_access_code)
