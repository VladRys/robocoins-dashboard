from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from models.student import Student

class StudentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_student_by_id(self, student_id: int) -> Student | None:
        """Fetch a student by their ID."""
        return await self.session.get(Student, student_id)

    async def change_balance(self, student_id: int, amount: int) -> int | None:
        """Atomically change a balance, rejecting changes that would make it negative."""
        result = await self.session.execute(
            update(Student)
            .where(
                Student.id == student_id,
                Student.balance + amount >= 0,
            )
            .values(balance=Student.balance + amount)
            .returning(Student.balance)
        )
        return result.scalar_one_or_none()

    async def get_student_by_hash_access_key(
        self, hash_access_key: str
    ) -> Student | None:
        """Fetch a student by their hash access key."""
        result = await self.session.execute(
            select(Student).where(Student.hash_access_key == hash_access_key)
        )
        return result.scalar_one_or_none()

    async def get_student_by_access_code(self, access_code: str) -> Student | None:
        """Fetch a student by their access code."""
        result = await self.session.execute(
            select(Student).where(Student.access_code == access_code)
        )
        return result.scalar_one_or_none()
    
    async def create_student(self, student: Student) -> Student:
        """Create a new student record."""
        self.session.add(student)
        await self.session.commit()
        await self.session.refresh(student)
        return student
    
    async def assign_student_to_group(self, student_id: int, group_id: int) -> Student | None:
        """Assign a student to a group."""
        student = await self.get_student_by_id(student_id)
        if student:
            student.group_id = group_id
            await self.session.commit()
            await self.session.refresh(student)
            return student
        return None