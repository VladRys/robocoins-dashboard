from fastapi import APIRouter, Depends, HTTPException

from models.group import Group
from schemas.group import GroupCreateRequest, GroupResponse
from schemas.student import StudentProfileResponse
from schemas.teacher import TeacherAssignmentRequest
from services.group import GroupService, get_group_service

group_router = APIRouter(
    prefix="/group",
    tags=["groups"],
)


def _group_response(group: Group) -> GroupResponse:
    return GroupResponse(
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


@group_router.post("/create", response_model=GroupResponse)
async def create_group(
    group: GroupCreateRequest,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    try:
        new_group = await service.create_group(group)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    if new_group is None:
        raise HTTPException(status_code=500, detail="Failed to create group")

    return _group_response(new_group)


@group_router.get("/id/{group_id}", response_model=GroupResponse)
async def get_group_by_id(
    group_id: int,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    group = await service.get_group_by_id(group_id)

    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    return _group_response(group)


@group_router.get("/name/{name}", response_model=GroupResponse)
async def get_group_by_name(
    name: str,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    group = await service.get_group_by_name(name)

    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    return _group_response(group)


@group_router.get("/course/{course_id}", response_model=list[GroupResponse])
async def get_groups_by_course_id(
    course_id: int,
    service: GroupService = Depends(get_group_service),
) -> list[GroupResponse]:
    groups = await service.get_groups_by_course_id(course_id)

    return [
        _group_response(group)
        for group in groups
    ]


@group_router.put("/id/{group_id}/teachers", response_model=GroupResponse)
async def assign_group_teachers(
    group_id: int,
    request: TeacherAssignmentRequest,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    try:
        group = await service.assign_group_teachers(group_id, request.teacher_ids)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    
    return _group_response(group)
