from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from models.group import Group
from models.user import User
from repositories.users import UserRepository


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.repository.get_user_by_id(user_id)

    async def get_users(self) -> list[User]:
        return await self.repository.get_users()

    async def get_user_by_access_code(self, access_code: str) -> User | None:
        return await self.repository.get_user_by_access_code(access_code)

    async def get_teacher_profile(
        self,
        user_id: int,
    ) -> tuple[User, list[Group]] | None:
        return await self.repository.get_teacher_profile(user_id)

    async def register_teacher(self, name: str) -> User:
        return await self.repository.create_teacher(name)


async def get_user_service(
    db: AsyncSession = Depends(get_db),
) -> UserService:
    return UserService(UserRepository(db))
