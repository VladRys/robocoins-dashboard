"""Idempotently add the demo groups and students to the configured PostgreSQL DB."""

import asyncio
import sys
import uuid
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
APP_DIR = BACKEND_DIR / "app"
sys.path[:0] = [str(APP_DIR), str(BACKEND_DIR)]

from sqlalchemy import select, text
from sqlalchemy.orm import selectinload

from app.core.access_code import generate_access_code
from app.core.config import Config
from app.core.database import SessionLocal, engine
from app.core.enums import CourseCategory, RewardType, UserRole
from app.models.course import Course
from app.models.group import Group
from app.models.reward import Reward
from app.models.session import Session  # noqa: F401
from app.models.student import Student
from app.models.teacher import Teacher  # noqa: F401
from app.models.transaction import BalanceTransaction  # noqa: F401
from app.models.user import User
from scripts.seed_daily_tasks import seed_daily_tasks

DEMO_GROUPS = (
    (
        "НД 16:00",
        "Arduino Junior",
        ("Анастасія Коваль", "Максим Шевченко", "Софія Бондар", "Данило Мельник", "Олена Ткаченко"),
    ),
    (
        "СР 18:00",
        "Middle Embedded",
        ("Іван Петренко", "Марія Кравець", "Артем Савчук", "Дарина Поліщук", "Богдан Лисенко"),
    ),
    (
        "СБ 12:00",
        "Unity 3D",
        ("Катерина Мороз", "Назар Клим", "Вікторія Романюк", "Михайло Олійник", "Юлія Ткач"),
    ),
)
DEMO_COURSE_CATEGORIES = {
    "Arduino Junior": CourseCategory.EMBEDDED,
    "Middle Embedded": CourseCategory.EMBEDDED,
    "Unity 3D": CourseCategory.GAME_DEV,
}

# Keep these IDs stable so the demo catalog matches the documented sample data.
DEMO_REWARDS = (
    (5, "Плата Arduino Nano", 70, "", RewardType.REWARD, CourseCategory.EMBEDDED),
    (7, "Музикальна пауза", 5, "Можливість обрати музику, яка буде грати під час виконання практики (В межах розумного)", RewardType.PRIVILEGE, None),
    (8, "Гідро-безліміт", 7, 'Безліміт на вийти "Попити води". Дійсний 2 занняття.', RewardType.PRIVILEGE, None),
    (9, "Uno-Reverse", 7, "Можливість переадресувати складне питання назад викладачу або передати іншому, лише за його згодою, дійсна 2-3 заняття", RewardType.PRIVILEGE, None),
    (10, "Унікальний аватар", 15, "Унікальний аватар на платформі", RewardType.PRIVILEGE, None),
    (14, "Тематичний лего-набір", 25, None, RewardType.REWARD, None),
    (13, "Червона кнопка", 15, "Таємна червона кнопка... (Аксессуар для клавіатури)", RewardType.REWARD, None),
    (3, "Набір компонентів", 40, "Набір компонентів які ти зможеш використати у власних проєктах.", RewardType.REWARD, CourseCategory.EMBEDDED),
    (12, "Трендові Клавіши", 15, "Брелок з трендовими клавішами", RewardType.REWARD, None),
    (1, "Випадковий стікер", 5, None, RewardType.REWARD, None),
    (2, "Стікер на вибір", 7, None, RewardType.REWARD, None),
    (6, "Набір Arduino Starter Kit", 100, "Приз Року!\nЙого отримає учень, якйи назбирає найбільше монет протягорм навчального року.\n\nНабір електроніки та компонентів, з яких ти вжеш зможеш зібрати власний проект. \nПлата: Arduino Uno", RewardType.REWARD, CourseCategory.EMBEDDED),
    (11, "Набір стикерів 100шт", 20, "Набір стікерів на тематику программування.", RewardType.REWARD, None),
    (15, "Гра в стимі", 70, "Будь яка гра гіфтом (До 225₴)", RewardType.REWARD, CourseCategory.GAME_DEV),
    (16, "Гра в стимі", 70, "Будь яка гра гіфтом (До 225₴)", RewardType.REWARD, CourseCategory.WEB),
)


async def unique_access_code(db) -> str:
    while True:
        code = generate_access_code()
        if await db.scalar(select(User.id).where(User.access_code == code)) is None:
            return code


async def align_sequence(db, table: str) -> None:
    """Advance a stale serial sequence without rewinding one already in use."""
    if table not in {"courses", "groups", "users", "rewards"}:
        raise ValueError(f"Unsupported sequence table: {table}")

    sequence = await db.scalar(
        text("SELECT pg_get_serial_sequence(:table_name, 'id')"),
        {"table_name": table},
    )
    if sequence is None:
        return

    last_value, is_called = (
        await db.execute(text(f"SELECT last_value, is_called FROM {sequence}"))
    ).one()
    max_id = await db.scalar(text(f"SELECT MAX(id) FROM {table}"))
    if max_id is not None and (last_value < max_id or not is_called):
        await db.execute(
            text("SELECT setval(pg_get_serial_sequence(:table_name, 'id'), :value, true)"),
            {"table_name": table, "value": max_id},
        )


async def seed_demo_data() -> tuple[int, int]:
    if not Config.DATABASE_URL.startswith(("postgresql+psycopg://", "postgresql+asyncpg://")):
        raise RuntimeError("Demo data can only be seeded into PostgreSQL")

    created_groups = 0
    created_students = 0

    async with SessionLocal() as db:
        async with db.begin():
            await align_sequence(db, "courses")
            await align_sequence(db, "groups")
            await align_sequence(db, "users")
            await seed_demo_rewards(db)
            await seed_daily_tasks(db)

            course_names = {course_name for _, course_name, _ in DEMO_GROUPS}
            courses = {
                course.name: course
                for course in (
                    await db.scalars(select(Course).where(Course.name.in_(course_names)))
                ).all()
            }
            for course_name in sorted(course_names - courses.keys()):
                course = Course(
                    name=course_name,
                    category=DEMO_COURSE_CATEGORIES[course_name],
                )
                db.add(course)
                courses[course_name] = course
            await db.flush()

            for group_name, course_name, student_names in DEMO_GROUPS:
                group = await db.scalar(
                    select(Group)
                    .options(selectinload(Group.students))
                    .where(Group.name == group_name)
                )

                if group is None:
                    group = Group(
                        name=group_name,
                        course_id=courses[course_name].id,
                        students=[],
                    )
                    db.add(group)
                    await db.flush()
                    created_groups += 1
                else:
                    # A same-named unrelated group is not safe to adopt as demo data.
                    existing_names = {student.name for student in group.students}
                    if not existing_names.intersection(student_names):
                        raise RuntimeError(
                            f"Group {group_name!r} already exists but does not look like demo data"
                        )

                existing_names = {student.name for student in group.students}
                for name in student_names:
                    if name in existing_names:
                        continue

                    access_code = await unique_access_code(db)
                    user = User(
                        name=name,
                        role=UserRole.STUDENT.value,
                        access_code=access_code,
                    )
                    db.add(user)
                    await db.flush()
                    db.add(
                        Student(
                            id=user.id,
                            user_id=user.id,
                            name=name,
                            avatar=None,
                            balance=0,
                            hash_access_key=uuid.uuid4().hex,
                            access_code=access_code,
                            groups=[group],
                        )
                    )
                    created_students += 1

    await engine.dispose()
    return created_groups, created_students


async def seed_demo_rewards(db) -> None:
    """Insert or update the fixed demo reward catalog by ID."""
    reward_ids = [reward_id for reward_id, *_ in DEMO_REWARDS]
    existing = {
        reward.id: reward
        for reward in (
            await db.scalars(select(Reward).where(Reward.id.in_(reward_ids)))
        ).all()
    }
    for reward_id, name, price, description, reward_type, category in DEMO_REWARDS:
        reward = existing.get(reward_id)
        if reward is None:
            reward = Reward(id=reward_id)
            db.add(reward)
        reward.name = name
        reward.price = price
        reward.description = description
        reward.type = reward_type
        reward.course_category = category
    await db.flush()
    await align_sequence(db, "rewards")


async def main() -> None:
    groups, students = await seed_demo_data()
    if groups == 0 and students == 0:
        print("Demo data is already present; nothing added.")
    else:
        print(f"Added {groups} groups and {students} students.")


if __name__ == "__main__":
    asyncio.run(main(), loop_factory=asyncio.SelectorEventLoop)
