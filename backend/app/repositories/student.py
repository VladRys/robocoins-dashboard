from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.student import Student

class StudentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_student_by_id(self, student_id: int) -> Student | None:
        """Fetch a student by their ID."""
        return await self.session.get(Student, student_id)

    async def get_student_by_hash_access_key(
        self, hash_access_key: str
    ) -> Student | None:
        """Fetch a student by their hash access key."""
        result = await self.session.execute(
            select(Student).where(Student.hash_access_key == hash_access_key)
        )
        return result.scalar_one_or_none()

    async def create_student(self, student: Student) -> Student:
        """Create a new student record."""
        self.session.add(student)
        await self.session.commit()
        await self.session.refresh(student)
        return student