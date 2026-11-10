import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import app.main
from app.core.database import Base
from app.core.enums import AchievementType
from app.models.achievement import Achievement, StudentAchievement
from app.models.student import Student
from app.models.user import User
from app.repositories.achievement import AchievementRepository
from app.repositories.student_achievement import StudentAchievementRepository


def test_achievement_and_student_achievement_repositories():
    async def run():
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        sessions = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with sessions() as session:
                session.add(
                    User(
                        id=1,
                        name="Student",
                        role="student",
                        access_code="USER-CODE",
                    )
                )
                session.add(
                    Student(
                        id=1,
                        user_id=1,
                        name="Student",
                        hash_access_key="student-hash",
                        access_code="STUDENT-CODE",
                    )
                )
                await session.commit()

                achievements = AchievementRepository(session)
                student_achievements = StudentAchievementRepository(session)
                badge = await achievements.create_achievement(
                    Achievement(
                        name="First steps",
                        description="Complete the first activity",
                        icon="star",
                        type=AchievementType.BADGE,
                        category="progress",
                    )
                )
                certificate = await achievements.create_achievement(
                    Achievement(
                        name="Champion",
                        description="Reach the top",
                        icon="trophy",
                        type=AchievementType.TROPHY,
                        category="competition",
                    )
                )

                assert await achievements.get_achievement_by_id(badge.id) == badge
                assert await achievements.get_achievement_by_id(-1) is None
                assert await achievements.get_all_achievements() == [badge, certificate]
                assert await achievements.get_achievements_by_category("progress") == [
                    badge
                ]
                assert await achievements.get_achievements_by_type(
                    AchievementType.TROPHY
                ) == [certificate]

                updated = await achievements.update_achievement(
                    badge.id,
                    name="First activity",
                    description="Finish an activity",
                )
                assert updated is badge
                assert badge.name == "First activity"
                assert badge.description == "Finish an activity"
                assert await achievements.update_achievement(-1, name="Missing") is None

                assignment = await student_achievements.add_student_achievement(
                    1,
                    badge.id,
                )
                assert assignment.student_id == 1
                assert assignment.achievement_id == badge.id
                assert await student_achievements.has_achievement(1, badge.id)
                assert await student_achievements.get_student_achievement(
                    1,
                    badge.id,
                ) == assignment
                assert await student_achievements.get_student_achievements(1) == [
                    assignment
                ]

                duplicate = await student_achievements.add_student_achievement(
                    1,
                    badge.id,
                )
                assert duplicate.student_id == assignment.student_id
                assert duplicate.achievement_id == assignment.achievement_id
                assignments = await session.scalars(
                    select(StudentAchievement).where(
                        StudentAchievement.student_id == 1
                    )
                )
                assert len(list(assignments.all())) == 1

                assert await student_achievements.remove_student_achievement(
                    1,
                    badge.id,
                )
                assert not await student_achievements.has_achievement(1, badge.id)
                assert not await student_achievements.remove_student_achievement(
                    1,
                    badge.id,
                )
                assert await achievements.delete_achievement(certificate.id)
                assert await achievements.get_achievement_by_id(certificate.id) is None
                assert not await achievements.delete_achievement(certificate.id)
        finally:
            await engine.dispose()

    asyncio.run(run())
