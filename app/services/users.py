from sqlalchemy.exc import IntegrityError
from app.models.group import Group
from app.models.user import User
from app.repositories.users import (
    GoogleAccountAlreadyLinkedError,
    UserRepository,
)


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.repository.get_user_by_id(user_id)

    async def get_users(self) -> list[User]:
        return await self.repository.get_users()

    async def get_user_by_access_code(self, access_code: str) -> User | None:
        return await self.repository.get_user_by_access_code(access_code)

    async def get_user_by_google_sub(self, google_sub: str) -> User | None:
        return await self.repository.get_user_by_google_sub(google_sub)

    async def link_google_account(
        self,
        user_id: int,
        google_sub: str,
        google_email: str,
    ) -> User:
        return await self.repository.link_google_account(
            user_id,
            google_sub,
            google_email,
        )

    async def unlink_google_account(self, user_id: int) -> User:
        return await self.repository.unlink_google_account(user_id)

    async def get_teacher_profile(
        self,
        user_id: int,
    ) -> tuple[User, list[Group]] | None:
        return await self.repository.get_teacher_profile(user_id)

    async def register_teacher(self, name: str) -> User:
        return await self.repository.create_teacher(name)

    async def get_or_create_admin_user(self) -> User:
        user = await self.repository.get_admin_user()
        if user is not None:
            return user
        try:
            return await self.repository.create_admin_user()
        except IntegrityError:
            # Another worker may have provisioned the single admin concurrently.
            user = await self.repository.get_admin_user()
            if user is None:
                raise
            return user


