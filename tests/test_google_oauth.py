import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import AsyncMock
from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi import FastAPI, Request
from sqlalchemy import func, select
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base
from app.models.achievement import Achievement, StudentAchievement
from app.models.course import Course
from app.models.daily_task import DailyTask
from app.models.google_oauth_state import GoogleOAuthState
from app.models.group import Group
from app.models.reward import Reward
from app.models.session import Session
from app.models.streak import Streak
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.transaction import BalanceTransaction
from app.models.user import User
from app.repositories.google_oauth import GoogleOAuthRepository, PendingGoogleOAuth
from app.repositories.users import GoogleAccountAlreadyLinkedError, UserRepository
from app.core.config import Config as cfg
from app.services.google_oauth import (
    GoogleIdentity,
    GoogleOAuthError,
    GoogleOAuthService,
)
from app.api.routes.auth import auth_router, google_oauth_callback


def test_google_identity_is_matched_only_by_subject(tmp_path: Path):
    async def run_test():
        engine = create_async_engine(
            URL.create("sqlite+aiosqlite", database=str(tmp_path / "google-users.db"))
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        try:
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)

            async with session_factory() as session:
                session.add(
                    User(
                        name="Existing account",
                        role="student",
                        access_code="STUDENT01",
                        google_email="same@gmail.com",
                    )
                )
                session.add(
                    User(
                        name="Second account",
                        role="teacher",
                        access_code="TEACHER01",
                    )
                )
                await session.commit()
                repository = UserRepository(session)

                assert await repository.get_user_by_google_sub("not-linked-sub") is None
                assert await session.scalar(select(func.count(User.id))) == 2

                first_user = await repository.get_user_by_access_code("STUDENT01")
                assert first_user is not None
                await repository.link_google_account(
                    user_id=first_user.id,
                    google_sub="linked-sub",
                    google_email="same@gmail.com",
                )
                linked = await repository.get_user_by_google_sub("linked-sub")
                assert linked is not None
                assert linked.id == first_user.id
                with pytest.raises(GoogleAccountAlreadyLinkedError):
                    second_user = await repository.get_user_by_access_code("TEACHER01")
                    assert second_user is not None
                    await repository.link_google_account(
                        user_id=second_user.id,
                        google_sub="linked-sub",
                        google_email="same@gmail.com",
                    )
                assert await session.scalar(select(func.count(User.id))) == 2
        finally:
            await engine.dispose()

    asyncio.run(run_test())


def test_google_oauth_state_is_one_time_and_expired_state_is_rejected(tmp_path: Path):
    async def run_test():
        engine = create_async_engine(
            URL.create("sqlite+aiosqlite", database=str(tmp_path / "google-state.db"))
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        try:
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)

            now = datetime.now(timezone.utc).replace(tzinfo=None)
            async with session_factory() as session:
                repository = GoogleOAuthRepository(session)
                await repository.create_state(
                    state_hash="a" * 64,
                    flow="login",
                    user_id=None,
                    nonce="nonce",
                    code_verifier="verifier",
                    expires_at=now + timedelta(minutes=5),
                )

                pending = await repository.consume_state("a" * 64, now)
                assert pending is not None
                assert pending.flow == "login"
                assert pending.user_id is None
                assert await repository.consume_state("a" * 64, now) is None

                await repository.create_state(
                    state_hash="b" * 64,
                    flow="login",
                    user_id=None,
                    nonce="nonce",
                    code_verifier="verifier",
                    expires_at=now - timedelta(seconds=1),
                )
                assert await repository.consume_state("b" * 64, now) is None
        finally:
            await engine.dispose()

    asyncio.run(run_test())


def test_google_login_does_not_create_an_unlinked_account():
    async def run_test():
        app = FastAPI()
        app.include_router(auth_router)
        request = Request(
            {
                "type": "http",
                "asgi": {"version": "3.0"},
                "http_version": "1.1",
                "method": "GET",
                "scheme": "https",
                "path": "/auth/google/callback",
                "raw_path": b"/auth/google/callback",
                "query_string": b"",
                "headers": [(b"cookie", b"google_oauth_state=state")],
                "client": ("127.0.0.1", 12345),
                "server": ("example.test", 443),
                "app": app,
            }
        )
        google_oauth = AsyncMock()
        google_oauth.consume_state.return_value = PendingGoogleOAuth(
            flow="login",
            user_id=None,
            nonce="nonce",
            code_verifier="verifier",
        )
        google_oauth.exchange_code.return_value = GoogleIdentity(
            sub="not-linked-sub",
            email="existing@gmail.com",
        )
        user_service = AsyncMock()
        user_service.get_user_by_google_sub.return_value = None
        student_service = AsyncMock()
        session_service = AsyncMock()

        response = await google_oauth_callback(
            request=request,
            code="authorization-code",
            state="state",
            google_oauth=google_oauth,
            user_service=user_service,
            student_service=student_service,
            session_service=session_service,
        )

        assert response.status_code == 303
        assert response.headers["location"].endswith("?google=not_linked")
        user_service.get_user_by_google_sub.assert_awaited_once_with("not-linked-sub")
        user_service.get_or_create_admin_user.assert_not_awaited()
        user_service.register_teacher.assert_not_awaited()
        session_service.create_session.assert_not_awaited()

    asyncio.run(run_test())


def test_google_callback_rejects_state_from_another_browser():
    async def run_test():
        app = FastAPI()
        app.include_router(auth_router)
        request = Request(
            {
                "type": "http",
                "asgi": {"version": "3.0"},
                "http_version": "1.1",
                "method": "GET",
                "scheme": "https",
                "path": "/auth/google/callback",
                "raw_path": b"/auth/google/callback",
                "query_string": b"",
                "headers": [(b"cookie", b"google_oauth_state=other-state")],
                "client": ("127.0.0.1", 12345),
                "server": ("example.test", 443),
                "app": app,
            }
        )
        google_oauth = AsyncMock()

        response = await google_oauth_callback(
            request=request,
            code="authorization-code",
            state="attacker-state",
            google_oauth=google_oauth,
            user_service=AsyncMock(),
            student_service=AsyncMock(),
            session_service=AsyncMock(),
        )

        assert response.status_code == 303
        assert response.headers["location"].endswith("?google=invalid_state")
        google_oauth.consume_state.assert_not_awaited()
        google_oauth.exchange_code.assert_not_awaited()

    asyncio.run(run_test())


def test_google_login_requests_explicit_account_selection(monkeypatch):
    async def run_test():
        repository = AsyncMock()
        service = GoogleOAuthService(repository)
        authorization = await service.create_authorization_url("login")
        query = parse_qs(urlsplit(authorization.url).query)

        assert query["prompt"] == ["select_account"]
        assert query["response_type"] == ["code"]
        assert query["scope"] == ["openid email profile"]
        assert query["code_challenge_method"] == ["S256"]
        repository.create_state.assert_awaited_once()
        assert repository.create_state.await_args.kwargs["flow"] == "login"
        assert repository.create_state.await_args.kwargs["user_id"] is None
        assert query["state"] == [authorization.state]

    monkeypatch.setattr(cfg, "GOOGLE_CLIENT_ID", "client-id")
    monkeypatch.setattr(cfg, "GOOGLE_CLIENT_SECRET", "client-secret")
    monkeypatch.setattr(cfg, "GOOGLE_REDIRECT_URI", "https://example.test/auth/google/callback")
    asyncio.run(run_test())


def test_google_identity_requires_matching_nonce_and_verified_email(monkeypatch):
    async def run_test():
        service = GoogleOAuthService(AsyncMock())
        claims = {
            "nonce": "expected-nonce",
            "sub": "google-sub",
            "email": "person@gmail.com",
            "email_verified": True,
        }
        monkeypatch.setattr(
            GoogleOAuthService,
            "_exchange_and_verify",
            staticmethod(lambda *args: claims),
        )
        identity = await service.exchange_code("code", "verifier", "expected-nonce")
        assert identity == GoogleIdentity(sub="google-sub", email="person@gmail.com")

        claims["nonce"] = "different-nonce"
        with pytest.raises(GoogleOAuthError):
            await service.exchange_code("code", "verifier", "expected-nonce")

        claims["nonce"] = "expected-nonce"
        claims["email_verified"] = False
        with pytest.raises(GoogleOAuthError):
            await service.exchange_code("code", "verifier", "expected-nonce")

    monkeypatch.setattr(cfg, "GOOGLE_CLIENT_ID", "client-id")
    monkeypatch.setattr(cfg, "GOOGLE_CLIENT_SECRET", "client-secret")
    monkeypatch.setattr(cfg, "GOOGLE_REDIRECT_URI", "https://example.test/auth/google/callback")
    asyncio.run(run_test())
