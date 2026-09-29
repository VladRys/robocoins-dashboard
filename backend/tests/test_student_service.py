import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from schemas.student import StudentCreateRequest
from services.student import StudentService


class FakeRepository:
    def __init__(self):
        self.saved = []

    async def create_student(self, student):
        self.saved.append(student)
        return student


def test_create_student_generates_unique_hash():
    async def run_test():
        repository = FakeRepository()
        service = StudentService(db=None, repository=repository)

        first_student = await service.create_student(
            StudentCreateRequest(name="Макс", group="Junior", avatar="🐯")
        )
        second_student = await service.create_student(
            StudentCreateRequest(name="Иван", group="Junior", avatar="🐻")
        )

        assert first_student.balance == 0
        assert first_student.name == "Макс"
        assert first_student.hash_access_key != second_student.hash_access_key

    asyncio.run(run_test())
