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
from app.models.course import Course
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
    "junior_robot_controller": {
        "type": "multiple_choice",
        "question": "Яка частина робота виконує програму та керує його компонентами?",
        "options": [
            "Контролер",
            "Датчик",
            "Виконавчий механізм",
            "Джерело живлення",
        ],
        "answer": "Контролер",
        "course_names": ["Arduino Junior"],
    },
    "junior_wiring_safety": {
        "type": "true_false",
        "question": "Перед зміною з'єднань у схемі Arduino безпечно вимкнути живлення.",
        "options": ["Так", "Ні"],
        "answer": "Так",
        "course_names": ["Arduino Junior"],
    },
    "junior_turnstile_servo": {
        "type": "text",
        "question": "Який компонент може повертати шлагбаум розумного турнікета?",
        "answer": "сервопривід",
        "course_names": ["Arduino Junior"],
    },
    "junior_smart_lamp": {
        "type": "multiple_choice",
        "question": "Який датчик допоможе розумній лампі вмикатися, коли в кімнаті темно?",
        "options": [
            "Фоторезистор",
            "Інфрачервоний датчик руху",
            "Датчик температури",
            "Ультразвуковий датчик відстані",
        ],
        "answer": "Фоторезистор",
        "course_names": ["Arduino Junior"],
    },
    "junior_joystick": {
        "type": "true_false",
        "question": "Джойстик можна використовувати для керування напрямком руху робота.",
        "options": ["Так", "Ні"],
        "answer": "Так",
        "course_names": ["Arduino Junior"],
    },
    "junior_seven_segment": {
        "type": "text",
        "question": "Скільки сегментів має стандартний семисегментний індикатор для цифр?",
        "answer": "7",
        "course_names": ["Arduino Junior"],
    },
    "middle_digital_write": {
        "type": "multiple_choice",
        "question": "Яку дію виконує digitalWrite(pin, HIGH) для цифрового піна?",
        "options": [
            "Встановлює високий логічний рівень",
            "Зчитує високий логічний рівень із піна",
            "Налаштовує пін як вихід",
            "Видає аналоговий сигнал із заданою шпаруватістю",
        ],
        "answer": "Встановлює високий логічний рівень",
        "course_names": ["Middle Embedded"],
    },
    "middle_array_indexing": {
        "type": "true_false",
        "question": "У C++ індекс першого елемента масиву дорівнює нулю.",
        "options": ["Так", "Ні"],
        "answer": "Так",
        "course_names": ["Middle Embedded"],
    },
    "middle_setup_function": {
        "type": "text",
        "question": "Як називається функція Arduino, яка виконується один раз під час запуску?",
        "answer": "setup",
        "course_names": ["Middle Embedded"],
    },
    "middle_loop_function": {
        "type": "multiple_choice",
        "question": "Яка функція Arduino повторюється постійно після завершення setup()?",
        "options": ["loop()", "setup()", "attachInterrupt()", "serialEvent()"],
        "answer": "loop()",
        "course_names": ["Middle Embedded"],
    },
    "middle_library_purpose": {
        "type": "true_false",
        "question": "Бібліотека в Arduino може містити готові функції для роботи з дисплеєм або датчиком.",
        "options": ["Так", "Ні"],
        "answer": "Так",
        "course_names": ["Middle Embedded"],
    },
    "middle_tinkercad_model": {
        "type": "text",
        "question": "У якій програмі з плану курсу створюють і тестують 3D-моделі електронних проєктів?",
        "answer": "Tinkercad",
        "course_names": ["Middle Embedded"],
    },
    "pro_pin_mode": {
        "type": "multiple_choice",
        "question": "Для чого в Arduino використовують pinMode()?",
        "options": [
            "Щоб налаштувати пін як вхід або вихід",
            "Щоб встановити на виході HIGH або LOW",
            "Щоб зчитати аналогове значення з піна",
            "Щоб вивести PWM-сигнал із заданою шпаруватістю",
        ],
        "answer": "Щоб налаштувати пін як вхід або вихід",
        "course_names": ["Pro Embedded"],
    },
    "pro_serial_monitor": {
        "type": "true_false",
        "question": "Монітор порту можна використовувати, щоб переглядати повідомлення, які програма надсилає через Serial.",
        "options": ["Так", "Ні"],
        "answer": "Так",
        "course_names": ["Pro Embedded"],
    },
    "pro_if_condition": {
        "type": "text",
        "question": "Яким ключовим словом у C++ починають умовний оператор?",
        "answer": "if",
        "course_names": ["Pro Embedded"],
    },
    "pro_lcd_display": {
        "type": "multiple_choice",
        "question": "Для чого в Arduino-проєкті використовують LCD?",
        "options": [
            "Щоб виводити текст або значення на екран",
            "Щоб зчитувати натискання кнопок через аналоговий вхід",
            "Щоб передавати дані між платою та комп'ютером через UART",
            "Щоб вимірювати рівень освітленості",
        ],
        "answer": "Щоб виводити текст або значення на екран",
        "course_names": ["Pro Embedded"],
    },
    "pro_array_zero_index": {
        "type": "true_false",
        "question": "У C++ перший елемент масиву має індекс 1.",
        "options": ["Так", "Ні"],
        "answer": "Ні",
        "course_names": ["Pro Embedded"],
    },
    "pro_arduino_language": {
        "type": "text",
        "question": "Яка мова програмування використовується в основах Arduino з плану Pro Embedded?",
        "answer": "C++",
        "course_names": ["Pro Embedded"],
    },
    "junior_sonar": {
        "type": "multiple_choice",
        "question": "Як сонар Arduino визначає відстань до перешкоди?",
        "options": [
            "Вимірює час повернення звукового сигналу",
            "Вимірює гучність відбитого сигналу",
            "Визначає частоту сигналу, відбитого від перешкоди",
            "Порівнює фазу сигналу на випромінювачі та приймачі",
        ],
        "answer": "Вимірює час повернення звукового сигналу",
        "course_names": ["Arduino Junior"],
    },
    "junior_analog_input": {
        "type": "multiple_choice",
        "question": "Яку величину зчитують з аналогового піна Arduino за допомогою analogRead()?",
        "options": [
            "Рівень аналогової напруги",
            "Час, протягом якого пін перебував у стані HIGH",
            "Шпаруватість PWM-сигналу на цьому піні",
            "Опір підключеного компонента в омах",
        ],
        "answer": "Рівень аналогової напруги",
        "course_names": ["Arduino Junior"],
    },
    "junior_relay": {
        "type": "true_false",
        "question": "Реле дає змогу керувати електричним колом за допомогою сигналу від Arduino.",
        "options": ["Так", "Ні"],
        "answer": "Так",
        "course_names": ["Arduino Junior"],
    },
    "middle_line_sensor": {
        "type": "multiple_choice",
        "question": "Для чого мобільній платформі потрібні датчики чорної лінії?",
        "options": [
            "Щоб визначати лінію на поверхні та рухатися вздовж неї",
            "Щоб визначати відстань до перешкоди попереду",
            "Щоб вимірювати швидкість обертання коліс",
            "Щоб визначати нахил корпусу платформи",
        ],
        "answer": "Щоб визначати лінію на поверхні та рухатися вздовж неї",
        "course_names": ["Middle Embedded"],
    },
    "middle_array_index": {
        "type": "multiple_choice",
        "question": "З якого індексу починається нумерація елементів масиву в C++?",
        "options": ["0", "1", "Розмір масиву", "-1"],
        "answer": "0",
        "course_names": ["Middle Embedded"],
    },
    "middle_game_collision": {
        "type": "true_false",
        "question": "У грі Arkanoid перевірка зіткнень потрібна, щоб визначити контакт м'яча з платформою або ціллю.",
        "options": ["Так", "Ні"],
        "answer": "Так",
        "course_names": ["Middle Embedded"],
    },
    "pro_nonblocking_timing": {
        "type": "multiple_choice",
        "question": "Чому замість довгих викликів delay() у проєкті Arduino часто використовують millis()?",
        "options": [
            "Щоб перевіряти час без зупинки виконання інших команд",
            "Щоб призупинити поточний потік виконання до заданого часу",
            "Щоб виміряти тривалість імпульсу з точністю до мікросекунд",
            "Щоб налаштувати апаратний таймер на періодичне переривання",
        ],
        "answer": "Щоб перевіряти час без зупинки виконання інших команд",
        "course_names": ["Pro Embedded"],
    },
    "pro_esp32_web_server": {
        "type": "multiple_choice",
        "question": "Яку роль виконує вебсервер на ESP32 у проєкті з керуванням через браузер?",
        "options": [
            "Приймає HTTP-запити від браузера та надсилає відповіді",
            "Ініціює HTTP-запити до браузера та чекає на відповіді",
            "Перетворює дані датчиків на HTML без обробки запитів",
            "Створює Wi-Fi-з'єднання між браузером і платою без мережевого протоколу",
        ],
        "answer": "Приймає HTTP-запити від браузера та надсилає відповіді",
        "course_names": ["Pro Embedded"],
    },
    "pro_blynk_chart": {
        "type": "multiple_choice",
        "question": "Для чого в Blynk використовують графік?",
        "options": [
            "Щоб бачити, як значення датчика змінюється з часом",
            "Щоб показувати лише останнє отримане значення датчика",
            "Щоб задавати вихідне значення віртуального піна",
            "Щоб надсилати сповіщення щоразу, коли змінюється значення",
        ],
        "answer": "Щоб бачити, як значення датчика змінюється з часом",
        "course_names": ["Pro Embedded"],
    },
}


async def seed_daily_tasks(db: AsyncSession) -> None:
    """Insert or update the demo daily-task question bank."""
    course_names = {
        course_name
        for task_data in TASKS.values()
        for course_name in task_data.get("course_names", [])
    }
    courses = (
        await db.scalars(select(Course).where(Course.name.in_(course_names)))
    ).all()
    courses_by_name = {course.name: course for course in courses}
    missing_courses = course_names - courses_by_name.keys()
    if missing_courses:
        raise RuntimeError(
            "Cannot seed course-specific daily tasks; missing courses: "
            + ", ".join(sorted(missing_courses))
        )

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
        question.course_ids = [
            courses_by_name[course_name].id
            for course_name in task_data.get("course_names", [])
        ]
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
