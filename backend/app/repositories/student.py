from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from models.student import Student
from models.group import Group
from models.user import User

class StudentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_student_by_id(self, student_id: int) -> Student | None:
        """Fetch a student by their ID."""
        result = await self.session.execute(
            select(Student)
            .options(selectinload(Student.groups))
            .where(Student.id == student_id)
        )
        return result.scalar_one_or_none()

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
            select(Student)
            .join(User, User.id == Student.user_id)
            .where(User.access_code == access_code)
        )
        return result.scalar_one_or_none()
    
    async def create_student(self, student: Student) -> Student:
        """Create a new student record."""
        self.session.add(student)
        await self.session.commit()
        await self.session.refresh(student)
        return student
    
    async def assign_student_to_groups(self, student_id: int, group_ids: list[int]) -> Student | None:
        """Replace a student's group assignments."""
        student = await self.get_student_by_id(student_id)
        if student is None:
            return None
        result = await self.session.execute(select(Group).where(Group.id.in_(group_ids)))
        groups = list(result.scalars().all())
        if len(groups) != len(set(group_ids)):
            raise ValueError("One or more groups were not found")
        student.groups = groups
        await self.session.commit()
        return await self.get_student_by_id(student_id)
