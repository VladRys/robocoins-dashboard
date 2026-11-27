from datetime import datetime, timezone

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.telegram_link_token import TelegramLinkToken
from app.models.user import User


class TelegramAccountAlreadyLinkedError(Exception):
    pass


class TelegramLinkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_linked_id(self, user_id: int) -> int | None:
        user = await self.session.get(User, user_id)
        return user.telegram_user_id if user else None

    async def create_token(
        self, user_id: int, token_hash: str, expires_at: datetime
    ) -> None:
        await self.session.execute(
            delete(TelegramLinkToken).where(
                (TelegramLinkToken.user_id == user_id)
                | (
                    TelegramLinkToken.expires_at
                    <= datetime.now(timezone.utc).replace(tzinfo=None)
                )
            )
        )
        self.session.add(
            TelegramLinkToken(
                user_id=user_id, token_hash=token_hash, expires_at=expires_at
            )
        )
        await self.session.commit()

    async def consume_token(
        self, token_hash: str, telegram_user_id: int, now: datetime
    ) -> str:
        token = await self.session.scalar(
            select(TelegramLinkToken).where(
                TelegramLinkToken.token_hash == token_hash
            )
        )
        if token is None:
            return "invalid"
        if token.expires_at <= now:
            await self.session.delete(token)
            await self.session.commit()
            return "expired"

        user_id = token.user_id
        try:
            result = await self.session.execute(
                update(User)
                .where(User.id == user_id, User.telegram_user_id.is_(None))
                .values(telegram_user_id=telegram_user_id)
            )
            await self.session.delete(token)
            if result.rowcount == 0:
                user = await self.session.get(User, user_id)
                if user is not None and user.telegram_user_id == telegram_user_id:
                    await self.session.commit()
                    return "already_linked"
                await self.session.rollback()
                return "account_already_linked"
            await self.session.commit()
            return "linked"
        except IntegrityError:
            await self.session.rollback()
            raise TelegramAccountAlreadyLinkedError from None

    async def unlink(self, user_id: int) -> None:
        user = await self.session.get(User, user_id)
        if user is not None:
            user.telegram_user_id = None
        await self.session.execute(
            delete(TelegramLinkToken).where(TelegramLinkToken.user_id == user_id)
        )
        await self.session.commit()
