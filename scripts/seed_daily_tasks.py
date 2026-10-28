"""Seed the demo daily-task question bank."""

import asyncio
import sys
from pathlib import Path
from urllib.parse import quote

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

PICTURE_OPTIONS = [
    "data:image/svg+xml," + quote(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 140">'
        '<path d="M18 70h38m108 0h38" stroke="#64748b" stroke-width="7"/>'
        '<rect x="55" y="46" width="110" height="48" rx="18" fill="#e8c99a" stroke="#a87943" stroke-width="5"/>'
        '<path d="M78 49v42m23-42v42m23-42v42m22-42v42" stroke="#a43d32" stroke-width="7"/>'
        "</svg>",
        safe="",
    ),
    "data:image/svg+xml," + quote(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 140">'
        '<path d="M92 79v40m36-40v40" stroke="#64748b" stroke-width="8"/>'
        '<path d="M110 20c-21 0-38 17-38 38 0 14 8 24 18 32h40c10-8 18-18 18-32 0-21-17-38-38-38Z" fill="#ef4444" stroke="#b91c1c" stroke-width="5"/>'
        "</svg>",
        safe="",
    ),
    "data:image/svg+xml," + quote(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 140">'
        '<path d="M74 91v29m72-29v29" stroke="#64748b" stroke-width="8"/>'
        '<rect x="50" y="42" width="120" height="62" rx="16" fill="#cbd5e1" stroke="#64748b" stroke-width="5"/>'
        '<rect x="70" y="22" width="80" height="61" rx="27" fill="#3b82f6" stroke="#1d4ed8" stroke-width="6"/>'
        "</svg>",
        safe="",
    ),
    "data:image/svg+xml," + quote(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 140">'
        '<path d="M28 105V65c0-22 18-40 40-40h84c22 0 40 18 40 40v40" stroke="#2563eb" stroke-width="16" fill="none"/>'
        '<path d="M18 104h20v22H18zm146 0h20v22h-20z" fill="#d1d5db" stroke="#64748b" stroke-width="4"/>'
        "</svg>",
        safe="",
    ),
]

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
        "question": "Обери світлодіод.",
        "options": PICTURE_OPTIONS,
        "answer": "1",
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
