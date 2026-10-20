from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.group import Group
from models.student import Student
from models.teacher import Teacher
from schemas.group import GroupCreateRequest

class GroupRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_group_by_id(self, group_id: int) -> Group | None:
        """Fetch a group by its ID."""
        result = await self.session.execute(
            select(Group)
            .options(
                selectinload(Group.students)
                .selectinload(Student.groups)
                .selectinload(Group.course)
            )
            .where(Group.id == group_id)
        )
        return result.scalar_one_or_none()
    
    async def create_group(self, group: GroupCreateRequest) -> Group:
        """Create a new group record."""
        db_group = Group(
            name=group.name,
            course_id=group.course_id,
            teacher_1_id=group.teacher_ids[0] if group.teacher_ids else None,
            teacher_2_id=group.teacher_ids[1] if len(group.teacher_ids) > 1 else None,
        )
        self.session.add(db_group)
        await self.session.commit()
        created_group = await self.get_group_by_id(db_group.id)
        if created_group is None:
            raise RuntimeError("Created group could not be loaded")
        return created_group

    async def get_existing_teacher_ids(self, teacher_ids: list[int]) -> set[int]:
        if not teacher_ids:
            return set()
        result = await self.session.execute(
            select(Teacher.user_id).where(Teacher.user_id.in_(teacher_ids))
        )
        return set(result.scalars().all())

    async def assign_group_teachers(
        self,
        group_id: int,
        teacher_ids: list[int],
    ) -> Group | None:
        group = await self.get_group_by_id(group_id)
        if group is None:
            return None
        group.teacher_1_id = teacher_ids[0] if teacher_ids else None
        group.teacher_2_id = teacher_ids[1] if len(teacher_ids) > 1 else None
        await self.session.commit()
        return group

    async def get_groups_by_course_id(self, course_id: int) -> list[Group]:
        """Fetch all groups associated with a specific course ID."""
        result = await self.session.execute(
            select(Group)
            .options(
                selectinload(Group.students)
                .selectinload(Student.groups)
                .selectinload(Group.course)
            )
            .where(Group.course_id == course_id)
        )
        return result.scalars().all()

    async def get_groups_by_teacher_and_course(
        self,
        teacher_id: int,
        course_id: int,
    ) -> list[Group]:
        result = await self.session.execute(
            select(Group)
            .options(selectinload(Group.students))
            .where(
                Group.course_id == course_id,
                (Group.teacher_1_id == teacher_id)
                | (Group.teacher_2_id == teacher_id),
            )
            .order_by(Group.id)
        )
        return list(result.scalars().all())

    async def get_groups_by_teacher(self, teacher_id: int) -> list[Group]:
        result = await self.session.execute(
            select(Group)
            .options(selectinload(Group.students))
            .where(
                (Group.teacher_1_id == teacher_id)
                | (Group.teacher_2_id == teacher_id),
            )
        )
        return list(result.scalars().all())
    
    async def get_group_by_name(self, name: str) -> Group | None:
        """Fetch a group by its name."""
        result = await self.session.execute(
            select(Group)
            .options(
                selectinload(Group.students)
                .selectinload(Student.groups)
                .selectinload(Group.course)
            )
            .where(Group.name == name)
        )
        return result.scalar_one_or_none()
