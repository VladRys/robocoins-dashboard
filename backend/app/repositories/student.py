import random
from sqlalchemy import select

from models.student import Student

class StudentRepository:
    def __init__(self, session):
        self.session = session

    async def get_student_by_id(self, student_id: int) -> Student:
        """Fetch a student by their ID."""
        return await self.session.get(Student, student_id)

    async def get_student_by_hash_access_key(self, hash_access_key: str) -> Student:
        """Fetch a student by their hash access key."""
        return await self.session.execute(
            select(Student).where(Student.hash_access_key == hash_access_key)
        ).scalar_one_or_none()


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
            

    async def create_student(self, student: Student) -> Student:
        """Create a new student record."""
        student.id = await self.generate_unique_student_id()
        self.session.add(student)
        await self.session.commit()
        await self.session.refresh(student)
        return student