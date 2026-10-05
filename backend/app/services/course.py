
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from repositories.course import CourseRepository


class CourseService:
    def __init__(self, course_repository: CourseRepository):
        self.course_repository = course_repository

    async def get_course_by_id(self, course_id):
        return await self.course_repository.get_course_by_id(course_id)

    async def create_course(self, course_data):
        return await self.course_repository.create_course(course_data)

    async def get_all_courses(self):
        return await self.course_repository.get_all_courses()


def get_course_service(db: AsyncSession = Depends(get_db)) -> CourseService:
    return CourseService(CourseRepository(db))