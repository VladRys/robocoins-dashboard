from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.achievement import StudentAchievement


class StudentAchievementRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_student_achievements(
        self, student_id: int
    ) -> list[StudentAchievement]:
        result = await self.session.execute(
            select(StudentAchievement)
            .where(StudentAchievement.student_id == student_id)
            .order_by(StudentAchievement.achievement_id)
        )
        return list(result.scalars().all())

    async def get_student_achievement_ids(self, student_id: int) -> set[int]:
        result = await self.session.scalars(
            select(StudentAchievement.achievement_id).where(
                StudentAchievement.student_id == student_id
            )
        )
        return set(result.all())

    async def get_student_achievement(
        self, student_id: int, achievement_id: int
    ) -> StudentAchievement | None:
        return await self.session.get(
            StudentAchievement,
            (student_id, achievement_id),
        )

    async def has_achievement(self, student_id: int, achievement_id: int) -> bool:
        result = await self.session.scalar(
            select(StudentAchievement.student_id).where(
                StudentAchievement.student_id == student_id,
                StudentAchievement.achievement_id == achievement_id,
            )
        )
        return result is not None

    async def add_student_achievement(
        self,
        student_id: int,
        achievement_id: int,
        *,
        commit: bool = True,
    ) -> StudentAchievement:
        assignment = await self.session.merge(
            StudentAchievement(
                student_id=student_id,
                achievement_id=achievement_id,
            )
        )
        if commit:
            await self.session.commit()
        else:
            await self.session.flush()
        return assignment

    async def remove_student_achievement(
        self, student_id: int, achievement_id: int
    ) -> bool:
        assignment = await self.get_student_achievement(student_id, achievement_id)
        if assignment is None:
            return False

        await self.session.delete(assignment)
        await self.session.commit()
        return True

    