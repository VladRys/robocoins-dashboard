from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.models.streak import Streak
from sqlalchemy import select

class StreakRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def start_streak(self, student_id: int) -> Streak:
        active = await self.db.execute(
            select(Streak).where(Streak.student_id == student_id, Streak.end_date.is_(None))
            .order_by(Streak.start_date.desc()).limit(1)
        )
        active_streak = active.scalar_one_or_none()
        if active_streak is not None:
            return active_streak
        streak = Streak(student_id=student_id, start_date=datetime.now(), days=0)
        self.db.add(streak)
        await self.db.commit()
        await self.db.refresh(streak)
        return streak
    
    async def end_streak(self, student_id: int) -> Streak | None:
        streak = await self.db.execute(
            select(Streak).where(Streak.student_id == student_id)
            .where(Streak.end_date.is_(None))
            .order_by(Streak.start_date.desc()).limit(1)
        )
        streak = streak.scalar_one_or_none()
        if streak:
            streak.end_date = datetime.now()
            streak.days = (streak.end_date - streak.start_date).days
            await self.db.commit()
            await self.db.refresh(streak)
            return streak
        return None

    async def prolong_streak(self, student_id: int) -> Streak | None:
        streak = await self.db.execute(
            select(Streak).where(Streak.student_id == student_id, Streak.end_date.is_(None))
            .order_by(Streak.start_date.desc()).limit(1)
        )
        streak = streak.scalar_one_or_none()
        if streak:
            streak.days = (datetime.now() - streak.start_date).days
            await self.db.commit()
            await self.db.refresh(streak)
            return streak
        return None


    async def get_streak(self, student_id: int) -> Streak | None:
        streak = await self.db.execute(
            select(Streak).where(Streak.student_id == student_id)
            .where(Streak.end_date.is_(None)).order_by(Streak.start_date.desc()).limit(1)
        )
        return streak.scalar_one_or_none()

    async def get_all_streaks(self) -> list[Streak]:
        streaks = await self.db.execute(select(Streak))
        return streaks.scalars().all()

    async def get_longest_streak(self, student_id: int) -> Streak | None:
        streaks = await self.db.execute(select(Streak).where(Streak.student_id == student_id).order_by(Streak.days.desc()).limit(1))
        return streaks.scalar_one_or_none()

    async def set_streak_days(self, student_id: int, days: int) -> Streak:
        streak = await self.db.execute(
            select(Streak).where(Streak.student_id == student_id, Streak.end_date.is_(None))
            .order_by(Streak.start_date.desc()).limit(1)
        )
        streak = streak.scalar_one_or_none()
        now = datetime.now()
        if streak is None:
            streak = Streak(
                student_id=student_id,
                start_date=now - timedelta(days=days),
                end_date=None,
                days=days,
            )
            self.db.add(streak)
        else:
            streak.days = days
            streak.start_date = now - timedelta(days=days)
            streak.end_date = None
        await self.db.commit()
        await self.db.refresh(streak)
        return streak
