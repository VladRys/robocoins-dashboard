from fastapi import APIRouter, Depends

from schemas.course import CourseResponse
from services.course import CourseService, get_course_service

course_router = APIRouter(
    prefix="/course",
    tags=["courses"],
)

@course_router.get("", response_model=list[CourseResponse])
async def get_courses(
    service: CourseService = Depends(get_course_service),
) -> list[CourseResponse]:
    courses = await service.get_all_courses()
    return [
        CourseResponse(
            id=course.id,
            name=course.name,
            groups=[group.id for group in course.groups],
            groups_count=len(course.groups),
        )
        for course in courses
    ]
