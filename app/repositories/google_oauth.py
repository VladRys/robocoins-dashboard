from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.google_oauth_state import GoogleOAuthState


@dataclass(frozen=True)
class PendingGoogleOAuth:
    flow: str
    user_id: int | None
    nonce: str
    code_verifier: str


class GoogleOAuthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_state(
        self,
        state_hash: str,
        flow: str,
        user_id: int | None,
        nonce: str,
        code_verifier: str,
        expires_at: datetime,
    ) -> None:
        await self.session.execute(
            delete(GoogleOAuthState).where(
                GoogleOAuthState.expires_at
                <= datetime.now(timezone.utc).replace(tzinfo=None)
            )
        )
        self.session.add(
            GoogleOAuthState(
                state_hash=state_hash,
                flow=flow,
                user_id=user_id,
                nonce=nonce,
                code_verifier=code_verifier,
                expires_at=expires_at,
            )
        )
        await self.session.commit()

    async def consume_state(
        self,
        state_hash: str,
        now: datetime,
    ) -> PendingGoogleOAuth | None:
        result = await self.session.execute(
            delete(GoogleOAuthState)
            .where(
                GoogleOAuthState.state_hash == state_hash,
                GoogleOAuthState.expires_at > now,
            )
            .returning(
                GoogleOAuthState.flow,
                GoogleOAuthState.user_id,
                GoogleOAuthState.nonce,
                GoogleOAuthState.code_verifier,
            )
        )
        row = result.one_or_none()
        await self.session.commit()
        if row is None:
            return None
        return PendingGoogleOAuth(
            flow=row.flow,
            user_id=row.user_id,
            nonce=row.nonce,
            code_verifier=row.code_verifier,
        )
