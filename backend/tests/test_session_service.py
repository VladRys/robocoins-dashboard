import asyncio
import hashlib
import sys
from pathlib import Path
from unittest.mock import AsyncMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from services.session import SessionService


def test_create_session_persists_hash_and_returns_raw_token():
    async def run_test():
        repository = AsyncMock()
        service = SessionService(repository)
        session_token = "raw-session-token"
        service._generate_session_token = AsyncMock(return_value=session_token)

        result = await service.create_session(student_id=123456)

        assert result == session_token
        repository.create_session.assert_awaited_once_with(
            123456,
            hashlib.sha256(session_token.encode("utf-8")).hexdigest(),
        )

    asyncio.run(run_test())


def test_session_lookup_and_delete_hash_presented_token():
    async def run_test():
        repository = AsyncMock()
        service = SessionService(repository)
        session_token = "raw-session-token"
        token_hash = hashlib.sha256(session_token.encode("utf-8")).hexdigest()

        await service.get_session_by_token(session_token)
        await service.delete_session(session_token)

        repository.get_session_by_token.assert_awaited_once_with(token_hash)
        repository.delete_session.assert_awaited_once_with(token_hash)

    asyncio.run(run_test())
