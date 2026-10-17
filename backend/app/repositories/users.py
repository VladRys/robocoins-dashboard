from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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

    async def create_teacher(self, name: str) -> User:
        user = User(name=name, role=UserRole.TEACHER.value)
        self.session.add(user)
        await self.session.flush()
        self.session.add(Teacher(user_id=user.id))
        await self.session.commit()
        await self.session.refresh(user)
        return user