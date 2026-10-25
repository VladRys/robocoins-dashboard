from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.group import Group
from app.models.teacher import Teacher
from app.models.user import User
from app.core.access_code import generate_access_code
from app.core.enums import UserRole


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_user_by_access_code(self, access_code: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.access_code == access_code)
        )
        return result.scalar_one_or_none()

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

    async def _generate_unique_access_code(self) -> str:
        while True:
            access_code = generate_access_code()
            exists = await self.session.scalar(
                select(User.id).where(User.access_code == access_code)
            )
            if exists is None:
                return access_code

    async def create_teacher(self, name: str) -> User:
        user = User(
            name=name,
            role=UserRole.TEACHER.value,
            access_code=await self._generate_unique_access_code(),
        )
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

    async def get_admin_user(self) -> User | None:
        result = await self.session.execute(
            select(User).where(User.role == UserRole.ADMIN.value).order_by(User.id)
        )
        return result.scalars().first()

    async def create_admin_user(self) -> User:
        user = User(
            name="Administrator",
            role=UserRole.ADMIN.value,
            access_code=await self._generate_unique_access_code(),
        )
        self.session.add(user)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
        await self.session.refresh(user)
        return user
