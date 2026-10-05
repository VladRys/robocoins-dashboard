from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.group import GroupCreateRequest, GroupResponse
from services.group import GroupService, get_group_service

group_router = APIRouter(
    prefix="/group",
    tags=["groups"],
)

@group_router.post("/create", response_model=GroupResponse)
async def create_group(
    group: GroupCreateRequest,
    db: AsyncSession = Depends(get_db),
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    new_group = await service.create_group(group)

    if new_group is None:
        raise HTTPException(status_code=500, detail="Failed to create group")

    return GroupResponse(
        id=new_group.id,
        name=new_group.name,
        course_id=new_group.course_id
    )
    
@group_router.get("/id/{group_id}", response_model=GroupResponse)
async def get_group_by_id(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    group = await service.get_group_by_id(group_id)

    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    return GroupResponse(
        id=group.id,
        name=group.name,
        course_id=group.course_id,
        students=[student.id for student in group.students],
        students_count=len(group.students),
    )

@group_router.get("/name/{name}", response_model=GroupResponse)
async def get_group_by_name(
    name: str,
    db: AsyncSession = Depends(get_db),
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    group = await service.get_group_by_name(name)

    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    return GroupResponse(
        id=group.id,
        name=group.name,
        course_id=group.course_id,
        students=[student.id for student in group.students],
        students_count=len(group.students),
    )
    
@group_router.get("/course/{course_id}", response_model=list[GroupResponse])
async def get_groups_by_course_id(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    service: GroupService = Depends(get_group_service),
) -> list[GroupResponse]:
    groups = await service.get_groups_by_course_id(course_id)

    return [
        GroupResponse(
            id=group.id,
            name=group.name,
            course_id=group.course_id,
            students=[student.id for student in group.students],
            students_count=len(group.students),
        )
        for group in groups
    ]
    
    