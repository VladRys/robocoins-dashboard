from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.course import Course


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
        result = await self.session.execute(select(Course))
        return result.scalars().all()
    
    