from models.course import Course

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class CourseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_course_by_id(self, course_id: int):
        """Fetch a course by its ID."""
        result = await self.session.execute(
            select(Course).where(Course.id == course_id)
        )
        return result.scalar_one_or_none()
    
    async def create_course(self, course: Course):
        """Create a new course record."""
        self.session.add(course)
        await self.session.commit()
        await self.session.refresh(course)
        return course
    
    async def get_all_courses(self):
        """Fetch all courses."""
        result = await self.session.execute(
            select(Course).options(selectinload(Course.groups))
        )
        return result.scalars().all()
    
    