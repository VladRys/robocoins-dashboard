from fastapi import APIRouter, Depends, HTTPException

from app.core.enums import CourseCategory
from schemas.course import CourseCreateRequest, CourseResponse
from schemas.group import GroupResponse
from schemas.student import StudentProfileResponse
from services.course import CourseService, get_course_service

course_router = APIRouter(
    prefix="/course",
    tags=["courses"],
)


def _course_response(course) -> CourseResponse:
    groups = [
        GroupResponse(
            id=group.id,
            name=group.name,
            course_id=group.course_id,
            students=[
                StudentProfileResponse.model_validate(student)
                for student in group.students
            ],
            students_count=len(group.students),
            teacher_ids=[
                teacher_id
                for teacher_id in (group.teacher_1_id, group.teacher_2_id)
                if teacher_id is not None
            ],
        )
        for group in course.groups
    ]
    return CourseResponse(
        id=course.id,
        name=course.name,
        category=course.category,
        groups=groups,
        groups_count=len(groups),
    )


@course_router.post("", response_model=CourseResponse, status_code=201)
async def create_course(
    course_data: CourseCreateRequest,
    service: CourseService = Depends(get_course_service),
) -> CourseResponse:
    try:
        course = await service.create_course(course_data)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return CourseResponse(
        id=course.id,
        name=course.name,
        category=course.category,
        groups=[],
        groups_count=0,
    )

@course_router.get("", response_model=list[CourseResponse])
async def get_courses(
    service: CourseService = Depends(get_course_service),
) -> list[CourseResponse]:
    courses = await service.get_all_courses()
    return [_course_response(course) for course in courses]


@course_router.get("/category/{category}", response_model=list[CourseResponse])
async def get_courses_by_category(
    category: CourseCategory,
    service: CourseService = Depends(get_course_service),
) -> list[CourseResponse]:
    courses = await service.get_courses_by_category(category)
    return [_course_response(course) for course in courses]
