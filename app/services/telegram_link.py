import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from app.repositories.telegram_link import TelegramLinkRepository


class TelegramLinkService:
    TOKEN_TTL = timedelta(minutes=10)

    def __init__(self, repository: TelegramLinkRepository):
        self.repository = repository

    async def create_link(self, user_id: int, bot_username: str) -> str:
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        expires_at = (datetime.now(timezone.utc) + self.TOKEN_TTL).replace(tzinfo=None)
        await self.repository.create_token(user_id, token_hash, expires_at)
        return f"https://t.me/{bot_username}?start={token}"

    async def consume_link(self, token: str, telegram_user_id: int) -> str:
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return await self.repository.consume_token(token_hash, telegram_user_id, now)

    async def get_linked_id(self, user_id: int) -> int | None:
        return await self.repository.get_linked_id(user_id)

    async def unlink(self, user_id: int) -> None:
        await self.repository.unlink(user_id)
