import asyncio
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from app.repositories.streak import StreakRepository


def result_with(value):
    return SimpleNamespace(scalar_one_or_none=lambda: value, scalars=lambda: SimpleNamespace(all=lambda: value))


def test_start_streak_creates_zero_day_streak_and_commits():
    async def run():
        db = SimpleNamespace(add=Mock(), execute=AsyncMock(return_value=result_with(None)), commit=AsyncMock(), refresh=AsyncMock())
        streak = await StreakRepository(db).start_streak(12)
        assert streak.student_id == 12
        assert streak.days == 0
        assert streak.end_date is None
        assert isinstance(streak.start_date, datetime)
        db.add.assert_called_once_with(streak)
        db.commit.assert_awaited_once()
        db.refresh.assert_awaited_once_with(streak)
    asyncio.run(run())


def test_start_streak_reuses_existing_active_streak():
    async def run():
        active_streak = SimpleNamespace(student_id=12, days=5, end_date=None)
        db = SimpleNamespace(
            add=Mock(),
            execute=AsyncMock(return_value=result_with(active_streak)),
            commit=AsyncMock(),
            refresh=AsyncMock(),
        )
        assert await StreakRepository(db).start_streak(12) is active_streak
        db.add.assert_not_called()
        db.commit.assert_not_awaited()

    asyncio.run(run())


def test_end_streak_ends_latest_streak_and_persists_days():
    async def run():
        streak = SimpleNamespace(start_date=datetime.now() - timedelta(days=4, hours=2), end_date=None, days=0)
        db = SimpleNamespace(
            execute=AsyncMock(return_value=result_with(streak)),
            commit=AsyncMock(), refresh=AsyncMock(),
        )
        ended = await StreakRepository(db).end_streak(12)
        assert ended is streak
        assert ended.end_date is not None
        assert ended.days == (ended.end_date - ended.start_date).days == 4
        db.commit.assert_awaited_once()
        db.refresh.assert_awaited_once_with(streak)
        assert "LIMIT" in str(db.execute.await_args.args[0]).upper()
    asyncio.run(run())


def test_get_streak_returns_none_when_student_has_no_streak():
    async def run():
        db = SimpleNamespace(execute=AsyncMock(return_value=result_with(None)))
        assert await StreakRepository(db).get_streak(12) is None
        assert "LIMIT" in str(db.execute.await_args.args[0]).upper()
    asyncio.run(run())


def test_prolong_streak_updates_day_count_without_ending_streak():
    async def run():
        streak = SimpleNamespace(
            start_date=datetime.now() - timedelta(days=2, hours=3),
            end_date=None,
            days=0,
        )
        db = SimpleNamespace(
            execute=AsyncMock(return_value=result_with(streak)),
            commit=AsyncMock(),
            refresh=AsyncMock(),
        )
        prolonged = await StreakRepository(db).prolong_streak(12)
        assert prolonged is streak
        assert prolonged.days == (datetime.now() - prolonged.start_date).days == 2
        assert prolonged.end_date is None
        db.commit.assert_awaited_once()
        db.refresh.assert_awaited_once_with(streak)

    asyncio.run(run())


def test_set_streak_days_creates_or_updates_current_streak():
    async def run():
        new_db = SimpleNamespace(
            execute=AsyncMock(return_value=result_with(None)),
            add=Mock(), commit=AsyncMock(), refresh=AsyncMock(),
        )
        created = await StreakRepository(new_db).set_streak_days(12, 9)
        assert created.days == 9
        assert created.end_date is None
        assert (datetime.now() - created.start_date).days == 9
        new_db.add.assert_called_once_with(created)
        new_db.commit.assert_awaited_once()

        existing = SimpleNamespace(start_date=datetime.now(), end_date=datetime.now(), days=2)
        update_db = SimpleNamespace(
            execute=AsyncMock(return_value=result_with(existing)),
            add=Mock(), commit=AsyncMock(), refresh=AsyncMock(),
        )
        updated = await StreakRepository(update_db).set_streak_days(12, 3)
        assert updated is existing
        assert updated.days == 3
        assert updated.end_date is None
        assert (datetime.now() - updated.start_date).days == 3
        update_db.add.assert_not_called()
        update_db.commit.assert_awaited_once()
    asyncio.run(run())
