from fastapi import APIRouter, Depends

from schemas.course import CourseResponse
from schemas.group import GroupResponse
from schemas.student import StudentProfileResponse
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
            groups=[
                GroupResponse(
                    id=group.id,
                    name=group.name,
                    course_id=group.course_id,
                    students=[StudentProfileResponse.model_validate(student) for student in group.students],
                    students_count=len(group.students),
                    teacher_ids=[
                        teacher_id
                        for teacher_id in (group.teacher_1_id, group.teacher_2_id)
                        if teacher_id is not None
                    ],
                )
                for group in course.groups
            ],
            groups_count=len(course.groups),
        )
        for course in courses
    ]
