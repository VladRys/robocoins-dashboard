import asyncio
import sys
from pathlib import Path

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from api.routes.course import get_courses
from api.routes.group import get_groups_by_course_id
from app.core.database import Base
from models.course import Course
from models.group import Group
from models.student import Student
from repositories.course import CourseRepository
from repositories.group import GroupRepository
from services.course import CourseService
from services.group import GroupService


def test_get_courses_returns_course_and_group_mapping(tmp_path: Path):
    async def run_test():
        engine = create_async_engine(
            URL.create("sqlite+aiosqlite", database=str(tmp_path / "courses.db")),
            pool_pre_ping=True,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        try:
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)

            async with session_factory() as session:
                course = Course(name="Python")
                session.add(course)
                await session.flush()
                session.add_all([
                    Group(name="Group A", course_id=course.id),
                    Group(name="Group B", course_id=course.id),
                ])
                await session.commit()

                response = await get_courses(
                    service=CourseService(CourseRepository(session))
                )

            assert len(response) == 1
            assert response[0].name == "Python"
            assert response[0].groups == [1, 2]
        finally:
            await engine.dispose()

    asyncio.run(run_test())


def test_get_groups_by_course_returns_groups_without_lazy_loading(tmp_path: Path):
    async def run_test():
        engine = create_async_engine(
            URL.create("sqlite+aiosqlite", database=str(tmp_path / "groups.db")),
            pool_pre_ping=True,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        try:
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)

            async with session_factory() as session:
                course = Course(name="Python")
                session.add(course)
                await session.flush()
                group = Group(name="Group A", course_id=course.id)
                session.add(group)
                await session.flush()
                session.add(Student(
                    id=123456,
                    name="Alex",
                    group_id=group.id,
                    course_name=course.name,
                    avatar="🤖",
                    balance=0,
                    hash_access_key="test-hash",
                    access_code="ABC12345",
                ))
                await session.commit()

                response = await get_groups_by_course_id(
                    course_id=course.id,
                    service=GroupService(session, GroupRepository(session)),
                )

            assert len(response) == 1
            assert response[0].name == "Group A"
            assert response[0].students == [123456]
            assert response[0].students_count == 1
        finally:
            await engine.dispose()

    asyncio.run(run_test())
