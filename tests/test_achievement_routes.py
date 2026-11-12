import asyncio
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.routes.achievement import (
    create_coin_earning_achievement,
    get_achievements,
)
from app.api.routes.student import get_student_achievement_progress
from app.core.database import Base
from app.core.enums import AchievementCategory, AchievementType
from app.models.achievement import Achievement, StudentAchievement
from app.models.student import Student
from app.models.transaction import BalanceTransaction
from app.models.user import User
from app.repositories.achievement import AchievementRepository
from app.repositories.student import StudentRepository
from app.repositories.student_achievement import StudentAchievementRepository
from app.repositories.transaction import TransactionRepository
from app.schemas.achievement import AchievementCreateRequest
from app.services.achievement import AchievementService
from app.services.student_achievement import StudentAchievementService


def test_admin_can_create_and_list_coin_earning_achievements(tmp_path: Path):
    async def run():
        engine = create_async_engine(
            URL.create(
                "sqlite+aiosqlite",
                database=str(tmp_path / "achievement-routes.db"),
            )
        )
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        sessions = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with sessions() as session:
                service = AchievementService(AchievementRepository(session))
                admin = User(id=10, name="Admin", role="admin", access_code="ADMIN001")
                request = AchievementCreateRequest(
                    name="Coin collector",
                    description="Earn 25 coins",
                    icon="🪙",
                    type=AchievementType.TROPHY,
                    required_coins=25,
                )
                created = await create_coin_earning_achievement(
                    request,
                    service,
                    admin,
                )
                listed = await get_achievements(service, admin)

                assert created.id > 0
                assert created.category == "coins_earning"
                assert created.required_coins == 25
                assert listed == [created]
        finally:
            await engine.dispose()

    asyncio.run(run())


def test_student_achievement_progress_requires_access_and_reports_threshold(
    tmp_path: Path,
):
    async def run():
        engine = create_async_engine(
            URL.create(
                "sqlite+aiosqlite",
                database=str(tmp_path / "achievement-progress.db"),
            )
        )
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        sessions = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with sessions() as session:
                user = User(id=20, name="Student", role="student", access_code="STU00001")
                session.add(user)
                await session.flush()
                session.add(
                    Student(
                        id=user.id,
                        user_id=user.id,
                        name=user.name,
                        hash_access_key="student-hash",
                        access_code="STU00002",
                    )
                )
                daily_task_achievement = Achievement(
                    name="Без пропусков",
                    description="Solve daily tasks correctly 5 days in a row",
                    icon="🔥",
                    type=AchievementType.BADGE,
                    category=AchievementCategory.DAILY_TASK_STREAK,
                )
                session.add_all(
                    [
                        Achievement(
                            name="First milestone",
                            description="Earn 4 coins",
                            icon="⭐",
                            type=AchievementType.BADGE,
                            category="coins_earning",
                            required_coins=4,
                        ),
                        daily_task_achievement,
                    ]
                )
                session.add(
                    BalanceTransaction(
                        student_id=user.id,
                        operation="deposit",
                        amount=3.0,
                        reason=["theory"],
                    )
                )
                await session.flush()
                session.add(
                    StudentAchievement(
                        student_id=user.id,
                        achievement_id=daily_task_achievement.id,
                    )
                )
                await session.commit()

                achievement_service = StudentAchievementService(
                    StudentAchievementRepository(session),
                    AchievementRepository(session),
                )
                authorization = SimpleNamespace(
                    is_allowed=AsyncMock(return_value=True)
                )
                result = await get_student_achievement_progress(
                    user.id,
                    StudentRepository(session),
                    achievement_service,
                    TransactionRepository(session),
                    authorization,
                    user,
                )
                assert result.earned_coins == 3.0
                assert len(result.achievements) == 1
                assert result.achievements[0].earned is False
                assert result.achievements[0].progress_percent == 75
                assert [
                    achievement.name
                    for achievement in result.earned_daily_task_achievements
                ] == ["Без пропусков"]

                authorization.is_allowed.return_value = False
                with pytest.raises(HTTPException) as error:
                    await get_student_achievement_progress(
                        user.id,
                        StudentRepository(session),
                        achievement_service,
                        TransactionRepository(session),
                        authorization,
                        user,
                    )
                assert error.value.status_code == 403
        finally:
            await engine.dispose()

    asyncio.run(run())
