from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.group import Group
from models.teacher import Teacher
from models.user import User
from app.core.enums import UserRole


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_users(self) -> list[User]:
        result = await self.session.execute(select(User).order_by(User.id))
        return list(result.scalars().all())

    async def get_teacher_profile(
        self,
        user_id: int,
    ) -> tuple[User, list[Group]] | None:
        user = await self.session.scalar(
            select(User).where(
                User.id == user_id,
                User.role == UserRole.TEACHER.value,
            )
        )
        if user is None:
            return None

        result = await self.session.execute(
            select(Group)
            .options(
                selectinload(Group.course),
                selectinload(Group.students),
            )
            .execution_options(populate_existing=True)
            .where(
                or_(
                    Group.teacher_1_id == user_id,
                    Group.teacher_2_id == user_id,
                )
            )
            .order_by(Group.id)
        )
        return user, list(result.scalars().all())

    async def create_teacher(self, name: str) -> User:
        user = User(name=name, role=UserRole.TEACHER.value)
        self.session.add(user)
        await self.session.flush()
        teacher_exists = await self.session.scalar(
            select(Teacher.user_id).where(Teacher.user_id == user.id)
        )
        if teacher_exists is None:
            self.session.add(Teacher(user_id=user.id))
        await self.session.commit()
        await self.session.refresh(user)
        return user