from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.group import GroupRepository
from schemas.group import GroupCreateRequest
from app.core.database import get_db

class GroupService:
    def __init__(self, db: AsyncSession, repository: GroupRepository):
        self.db = db
        self.repository = repository

    async def get_group_by_id(self, group_id: int):
        return await self.repository.get_group_by_id(group_id)
    
    async def create_group(self, request: GroupCreateRequest):
        await self._validate_teacher_ids(request.teacher_ids)
        return await self.repository.create_group(request)
    
    async def get_groups_by_course_id(self, course_id: int):
        return await self.repository.get_groups_by_course_id(course_id)
    
    async def get_group_by_name(self, name: str):
        return await self.repository.get_group_by_name(name)

    async def assign_group_teachers(self, group_id: int, teacher_ids: list[int]):
        await self._validate_teacher_ids(teacher_ids)
        return await self.repository.assign_group_teachers(group_id, teacher_ids)

    async def _validate_teacher_ids(self, teacher_ids: list[int]) -> None:
        if len(teacher_ids) > 2:
            raise ValueError("A group can have at most two teachers")
        if len(set(teacher_ids)) != len(teacher_ids):
            raise ValueError("Teacher IDs must be unique")
        existing_ids = await self.repository.get_existing_teacher_ids(teacher_ids)
        if existing_ids != set(teacher_ids):
            raise ValueError("One or more teachers were not found")
    
def get_group_service(db: AsyncSession = Depends(get_db)) -> GroupService:
    repository = GroupRepository(db)
    return GroupService(db, repository)