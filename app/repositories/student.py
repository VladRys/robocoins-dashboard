from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import case, select, update
from sqlalchemy.orm import selectinload

from app.models.student import Student
from app.models.group import Group
from app.models.user import User

class StudentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_student_by_id(self, student_id: int) -> Student | None:
        """Fetch a student by their ID."""
        result = await self.session.execute(
            select(Student)
            .options(selectinload(Student.groups).selectinload(Group.course))
            .where(Student.id == student_id)
        )
        return result.scalar_one_or_none()

    async def change_balance(self, student_id: int, amount: int) -> int | None:
        """Atomically change a balance without allowing it to fall below zero."""
        result = await self.session.execute(
            update(Student)
            .where(Student.id == student_id)
            .values(
                balance=case(
                    (Student.balance + amount < 0, 0),
                    else_=Student.balance + amount,
                )
            )
            .returning(Student.balance)
        )
        return result.scalar_one_or_none()

    async def reverse_balance_transaction(
        self,
        student_id: int,
        operation: str,
        amount: int,
    ) -> int | None:
        """Reverse a ledger operation, refusing to overdraw a prior deposit."""
        delta = -amount if operation == "deposit" else amount
        statement = update(Student).where(Student.id == student_id)
        if delta < 0:
            statement = statement.where(Student.balance >= amount)
        result = await self.session.execute(
            statement.values(balance=Student.balance + delta).returning(Student.balance)
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
        # Reload relationships explicitly before the API builds its response.
        # Accessing unloaded relationships here can trigger async lazy loading
        # outside SQLAlchemy's greenlet context.
        created_student = await self.get_student_by_id(student.id)
        if created_student is None:
            raise RuntimeError("Student was not available after being created")
        return created_student
    
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
