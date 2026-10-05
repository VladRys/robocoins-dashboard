from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.group import GroupRepository
from schemas.group import GroupCreateRequest
from core.database import get_db

class GroupService:
    def __init__(self, db: AsyncSession, repository: GroupRepository):
        self.db = db
        self.repository = repository

    async def get_group_by_id(self, group_id: int):
        return await self.repository.get_group_by_id(group_id)
    
    async def create_group(self, request: GroupCreateRequest):
        return await self.repository.create_group(request)
    
    async def get_groups_by_course_id(self, course_id: int):
        return await self.repository.get_groups_by_course_id(course_id)
    
    async def get_group_by_name(self, name: str):
        return await self.repository.get_group_by_name(name)
    
def get_group_service(db: AsyncSession = Depends(get_db)) -> GroupService:
    repository = GroupRepository(db)
    return GroupService(db, repository)