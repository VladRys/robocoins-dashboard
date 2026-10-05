
from backend.app.repositories.course import CourseRepository
from backend.app.models.course import Course
from backend.app.core.database import get_db
from fastapi import Depends


class CourseService:
    def __init__(self, course_repository: CourseRepository):
        self.course_repository = course_repository

    async def get_course_by_id(self, course_id):
        return await self.course_repository.get_course_by_id(course_id)

    async def create_course(self, course_data):
        return await self.course_repository.create_course(course_data)

    async def get_all_courses(self):
        return await self.course_repository.get_all_courses()