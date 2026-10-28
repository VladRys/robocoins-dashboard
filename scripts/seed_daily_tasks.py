"""Seed the demo daily-task question bank."""

import asyncio
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
APP_DIR = BACKEND_DIR / "app"
sys.path[:0] = [str(APP_DIR), str(BACKEND_DIR)]

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Config
from app.core.database import SessionLocal, engine
from app.core.enums import TaskType
from app.models.course import Course  # noqa: F401
from app.models.daily_task import DailyTask, DailyTaskQuestion
from app.models.group import Group  # noqa: F401
from app.models.session import Session  # noqa: F401
from app.models.student import Student  # noqa: F401
from app.models.streak import Streak  # noqa: F401
from app.models.teacher import Teacher  # noqa: F401
from app.models.transaction import BalanceTransaction  # noqa: F401
from app.models.user import User  # noqa: F401

TASKS: dict[str, dict] = {
    "mc_led": {
        "type": "multiple_choice",
        "question": "Який компонент випромінює світло?",
        "options": ["Резистор", "Світлодіод", "Кнопка", "Дріт"],
        "answer": "Світлодіод",
    },
    "mc_sensor": {
        "type": "multiple_choice",
        "question": "Який датчик вимірює відстань за допомогою звуку?",
        "options": [
            "Ультразвуковий",
            "Датчик температури",
            "Фоторезистор",
            "Гіроскоп",
        ],
        "answer": "Ультразвуковий",
    },
    "mc_loop": {
        "type": "multiple_choice",
        "question": "Що робить цикл у програмі?",
        "options": [
            "Повторює команди",
            "Вимикає комп'ютер",
            "Змінює колір екрана",
            "Видаляє програму",
        ],
        "answer": "Повторює команди",
    },
    "tf_voltage": {
        "type": "true_false",
        "question": "Для роботи світлодіода важливо дотримуватися полярності.",
        "options": ["Так", "Ні"],
        "answer": "Так",
    },
    "tf_motor": {
        "type": "true_false",
        "question": "Електродвигун може перетворювати електричну енергію на рух.",
        "options": ["Так", "Ні"],
        "answer": "Так",
    },
    "text_python": {
        "type": "text",
        "question": "Яким словом у Python починають умовну команду?",
        "answer": "if",
    },
    "text_robot": {
        "type": "text",
        "question": "Як називається набір команд, який виконує робот?",
        "answer": "програма",
    },
    "picture_led": {
        "type": "picture",
        "question": "Натисни на світлодіод.",
        "image_url": "/student/daily-task/assets/components.svg",
        "hotspots": [
            {"id": "led", "x": 268, "y": 63, "width": 104, "height": 104}
        ],
        "answer": "led",
    },
}


async def seed_daily_tasks(db: AsyncSession) -> None:
    """Insert or update the demo daily-task question bank."""
    for slug, task_data in TASKS.items():
        question = await db.scalar(
            select(DailyTaskQuestion).where(DailyTaskQuestion.slug == slug)
        )
        if question is None:
            question = DailyTaskQuestion(
                slug=slug,
                question=task_data["question"],
                task_type=TaskType(task_data["type"]),
                answer=task_data["answer"],
            )
            db.add(question)

        question.question = task_data["question"]
        question.task_type = TaskType(task_data["type"])
        question.options = task_data.get("options")
        question.course_categories = task_data.get("course_categories", [])
        question.answer = task_data["answer"]
        question.reward = task_data.get("reward", Config.DAILY_TASK_REWARD)
        question.image_url = task_data.get("image_url")
        question.hotspots = task_data.get("hotspots")
        await db.flush()

        daily_task = await db.scalar(
            select(DailyTask).where(DailyTask.question_id == question.id)
        )
        if daily_task is None:
            db.add(DailyTask(question_id=question.id))
    await db.flush()


async def main() -> None:
    if not Config.DATABASE_URL.startswith(
        ("postgresql+psycopg://", "postgresql+asyncpg://")
    ):
        raise RuntimeError("Daily tasks can only be seeded into PostgreSQL")

    async with SessionLocal() as db:
        async with db.begin():
            await seed_daily_tasks(db)

    await engine.dispose()
    print(f"Seeded {len(TASKS)} daily task questions.")


if __name__ == "__main__":
    asyncio.run(main(), loop_factory=asyncio.SelectorEventLoop)
