from app.models.course import Course
from app.models.group import Group
from app.models.student import Student
from app.core.enums import CourseCategory

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.schemas.course import CourseCreateRequest


class CourseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_course_by_id(self, course_id: int):
        """Fetch a course by its ID."""
        result = await self.session.execute(
            select(Course).where(Course.id == course_id)
        )
        return result.scalar_one_or_none()
    
    async def create_course(self, course_data: CourseCreateRequest) -> Course:
        """Create a new course record."""
        course = Course(name=course_data.name, category=course_data.category)
        self.session.add(course)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise ValueError("A course with this name already exists") from None
        await self.session.refresh(course)
        return course
    
    async def get_all_courses(self):
        """Fetch all courses."""
        result = await self.session.execute(
            select(Course).options(
                selectinload(Course.groups)
                .selectinload(Group.students)
                .selectinload(Student.groups)
                .selectinload(Group.course)
            )
        )
        return result.scalars().all()

    async def get_courses_by_category(self, category: CourseCategory):
        result = await self.session.execute(
            select(Course)
            .options(
                selectinload(Course.groups)
                .selectinload(Group.students)
                .selectinload(Student.groups)
                .selectinload(Group.course)
            )
            .where(Course.category == category)
        )
        return result.scalars().all()
    
    
