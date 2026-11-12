import asyncio

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models.achievement import Achievement
from scripts.seed_demo_data import DEMO_ACHIEVEMENTS, seed_demo_achievements


def test_seed_demo_achievements_is_idempotent():
    async def run():
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as connection:
            await connection.run_sync(Achievement.__table__.create)

        sessions = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with sessions() as session:
                await seed_demo_achievements(session)
                await session.commit()
                await seed_demo_achievements(session)
                await session.commit()

                achievements = list(
                    (
                        await session.scalars(
                            select(Achievement).order_by(Achievement.id)
                        )
                    ).all()
                )
                assert await session.scalar(
                    select(func.count()).select_from(Achievement)
                ) == len(DEMO_ACHIEVEMENTS)
                assert [
                    (
                        achievement.id,
                        achievement.category,
                        achievement.required_coins,
                    )
                    for achievement in achievements
                ] == [
                    (achievement_id, category, required_coins)
                    for achievement_id, category, _, _, _, _, required_coins
                    in DEMO_ACHIEVEMENTS
                ]
        finally:
            await engine.dispose()

    asyncio.run(run())
