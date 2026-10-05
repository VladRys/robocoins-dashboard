from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.group import Group
from schemas.group import GroupCreateRequest

class GroupRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_group_by_id(self, group_id: int) -> Group | None:
        """Fetch a group by its ID."""
        result = await self.session.execute(
            select(Group)
            .options(selectinload(Group.students))
            .where(Group.id == group_id)
        )
        return result.scalar_one_or_none()
    
    async def create_group(self, group: GroupCreateRequest) -> Group:
        """Create a new group record."""
        db_group = Group(
            name=group.name,
            course_id=group.course_id,
        )
        self.session.add(db_group)
        await self.session.commit()
        await self.session.refresh(db_group)
        return db_group

    async def get_groups_by_course_id(self, course_id: int) -> list[Group]:
        """Fetch all groups associated with a specific course ID."""
        result = await self.session.execute(
            select(Group)
            .options(selectinload(Group.students))
            .where(Group.course_id == course_id)
        )
        return result.scalars().all()
    
    async def get_group_by_name(self, name: str) -> Group | None:
        """Fetch a group by its name."""
        result = await self.session.execute(
            select(Group)
            .options(selectinload(Group.students))
            .where(Group.name == name)
        )
        return result.scalar_one_or_none()