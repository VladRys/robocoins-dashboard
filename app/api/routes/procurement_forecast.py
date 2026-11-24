from datetime import date, timedelta
from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_authenticated_admin, get_db
from app.models.user import User


procurement_forecast_router = APIRouter(tags=["procurement forecast"])
PAGE_PATH = Path(__file__).resolve().parents[3] / "pages" / "procurement-forecast.html"
ADMIN_PAGE_PATH = PAGE_PATH.with_name("admin-test.html")
FORECAST_END = date(2026, 12, 27)
DAILY_TASK_REWARD = 0.1
COINS_PER_LESSON = 3


@procurement_forecast_router.get("/procurement-forecast", include_in_schema=False)
async def procurement_forecast_page() -> FileResponse:
    return FileResponse(PAGE_PATH)


@procurement_forecast_router.get("/admin-test.html", include_in_schema=False)
async def admin_test_page() -> FileResponse:
    return FileResponse(ADMIN_PAGE_PATH)


@procurement_forecast_router.get("/procurement-forecast/data")
async def get_procurement_forecast(
    _admin: User = Depends(get_authenticated_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    today = date.today()
    forecast_days = max(0, (FORECAST_END - today).days)

    def weekly_sessions(weekday: int) -> int:
        first = today + timedelta(days=(weekday - today.isoweekday()) % 7)
        if first <= today:
            first += timedelta(days=7)
        total = 0
        while first <= FORECAST_END:
            total += 1
            first += timedelta(days=7)
        return total

    saturday_sessions = weekly_sessions(6)
    sunday_sessions = weekly_sessions(7)

    student_rows = (
        await db.execute(
            text(
                """
                WITH excluded_students AS (
                    SELECT DISTINCT sg.student_id
                    FROM student_groups sg
                    JOIN groups g ON g.id = sg.group_id
                    JOIN courses c ON c.id = g.course_id
                    WHERE c.name = 'Senior Embedded'
                ), history AS (
                    SELECT MIN(created_at::date) AS first_day,
                           MAX(created_at::date) AS last_day
                    FROM balance_transactions
                    WHERE operation = 'deposit' AND cancelled_at IS NULL
                      AND student_id NOT IN (SELECT student_id FROM excluded_students)
                ), earned AS (
                    SELECT student_id, SUM(amount) AS coins
                    FROM balance_transactions
                    WHERE operation = 'deposit'
                      AND cancelled_at IS NULL
                      AND student_id NOT IN (SELECT student_id FROM excluded_students)
                      AND created_at::date BETWEEN
                          (SELECT first_day FROM history)
                          AND (SELECT last_day FROM history)
                    GROUP BY student_id
                ), daily_earned AS (
                    SELECT sdt.student_id, SUM(question.reward) AS coins
                    FROM student_daily_tasks sdt
                    JOIN daily_tasks task ON task.id = sdt.daily_task_id
                    JOIN daily_task_questions question ON question.id = task.question_id
                    WHERE sdt.correct IS TRUE
                      AND sdt.completed_at::date BETWEEN
                          (SELECT first_day FROM history)
                          AND (SELECT last_day FROM history)
                      AND sdt.student_id NOT IN (SELECT student_id FROM excluded_students)
                    GROUP BY sdt.student_id
                ), enrolled AS (
                    SELECT sg.student_id,
                           COUNT(*) FILTER (WHERE g.name ILIKE 'СБ%') AS saturday_groups,
                           COUNT(*) FILTER (WHERE g.name ILIKE 'НД%') AS sunday_groups,
                           BOOL_OR(c.category = 'embedded') AS embedded,
                           BOOL_OR(c.category = 'game dev') AS game_dev,
                           BOOL_OR(c.category = 'web') AS web,
                           BOOL_OR(c.category = 'python') AS python,
                           BOOL_OR(c.category = 'primary') AS primary_course
                    FROM student_groups sg
                    JOIN groups g ON g.id = sg.group_id
                    JOIN courses c ON c.id = g.course_id
                    WHERE c.name <> 'Senior Embedded'
                    GROUP BY sg.student_id
                )
                SELECT s.id, s.balance, COALESCE(e.coins, 0) AS earned,
                       COALESCE(daily.coins, 0) AS daily_earned,
                       COALESCE(en.saturday_groups, 0) AS saturday_groups,
                       COALESCE(en.sunday_groups, 0) AS sunday_groups,
                       (en.student_id IS NOT NULL) AS has_group,
                       COALESCE(en.embedded, FALSE) AS embedded,
                       COALESCE(en.game_dev, FALSE) AS game_dev,
                       COALESCE(en.web, FALSE) AS web,
                       COALESCE(en.python, FALSE) AS python,
                       COALESCE(en.primary_course, FALSE) AS primary_course
                FROM students s
                LEFT JOIN earned e ON e.student_id = s.id
                LEFT JOIN daily_earned daily ON daily.student_id = s.id
                LEFT JOIN enrolled en ON en.student_id = s.id
                WHERE s.id NOT IN (SELECT student_id FROM excluded_students)
                """
            )
        )
    ).mappings().all()

    history_row = (
        await db.execute(
            text(
                """
                SELECT MIN(created_at::date) AS first_day,
                       MAX(created_at::date) AS last_day,
                       COUNT(*) AS deposit_count,
                       COALESCE(SUM(amount), 0) AS deposited
                FROM balance_transactions
                WHERE operation = 'deposit' AND cancelled_at IS NULL
                  AND student_id NOT IN (
                      SELECT DISTINCT sg.student_id
                      FROM student_groups sg
                      JOIN groups g ON g.id = sg.group_id
                      JOIN courses c ON c.id = g.course_id
                      WHERE c.name = 'Senior Embedded'
                  )
                """
            )
        )
    ).mappings().one()
    history_days = (
        max(1, (history_row["last_day"] - history_row["first_day"]).days + 1)
        if history_row["first_day"] and history_row["last_day"]
        else 0
    )

    rewards = (
        await db.execute(
            text(
                """
                SELECT id, name, price, type, course_category
                FROM rewards
                WHERE type = 'reward'
                ORDER BY price, name
                """
            )
        )
    ).mappings().all()

    forecast_students = []
    for student in student_rows:
        balance = float(student["balance"])
        earned = float(student["earned"])
        daily_earned = float(student["daily_earned"])
        expected = balance + (earned / history_days * forecast_days if history_days else 0)
        expected_without_daily_tasks = balance + (
            max(0.0, earned - daily_earned) / history_days * forecast_days
            if history_days
            else 0
        )
        lesson_count = (
            int(student["saturday_groups"]) * saturday_sessions
            + int(student["sunday_groups"]) * sunday_sessions
        )
        theoretical = balance + forecast_days * DAILY_TASK_REWARD
        theoretical += lesson_count * COINS_PER_LESSON
        forecast_students.append(
            {
                "balance": balance,
                "expected": expected,
                "expected_without_daily_tasks": expected_without_daily_tasks,
                "theoretical": theoretical,
                "has_group": bool(student["has_group"]),
                "lesson_count": lesson_count,
                "categories": {
                    "embedded": student["embedded"],
                    "game dev": student["game_dev"],
                    "web": student["web"],
                    "python": student["python"],
                    "primary": student["primary_course"],
                },
            }
        )

    count = len(forecast_students)
    if count:
        averages = {
            field: round(sum(s[field] for s in forecast_students) / count, 2)
            for field in (
                "balance",
                "expected",
                "expected_without_daily_tasks",
                "theoretical",
            )
        }
    else:
        averages = {
            "balance": 0,
            "expected": 0,
            "expected_without_daily_tasks": 0,
            "theoretical": 0,
        }

    def eligible_for_category(student: dict, category: str | None) -> bool:
        return category is None or student["categories"].get(category, False)

    reward_report = []
    for reward in rewards:
        eligible = [
            student
            for student in forecast_students
            if eligible_for_category(student, reward["course_category"])
        ]
        price = float(reward["price"])
        reward_report.append(
            {
                "id": reward["id"],
                "name": reward["name"],
                "price": reward["price"],
                "category": reward["course_category"],
                "eligible_students": len(eligible),
                "can_afford_now": sum(s["balance"] >= price for s in eligible),
                "can_afford_expected": sum(s["expected"] >= price for s in eligible),
                "can_afford_without_daily_tasks": sum(
                    s["expected_without_daily_tasks"] >= price for s in eligible
                ),
                "can_afford_theoretical": sum(s["theoretical"] >= price for s in eligible),
            }
        )

    return {
        "as_of": today.isoformat(),
        "forecast_start": today.isoformat(),
        "forecast_end": FORECAST_END.isoformat(),
        "forecast_days": forecast_days,
        "students": count,
        "students_with_groups": sum(s["has_group"] for s in forecast_students),
        "excluded_course": "Senior Embedded",
        "averages": averages,
        "history": {
            "from": history_row["first_day"].isoformat() if history_row["first_day"] else None,
            "to": history_row["last_day"].isoformat() if history_row["last_day"] else None,
            "days": history_days,
            "deposit_count": history_row["deposit_count"],
            "coins": round(float(history_row["deposited"]), 1),
            "daily_task_coins": round(
                sum(float(student["daily_earned"]) for student in student_rows), 1
            ),
            "average_daily_per_student": (
                round(float(history_row["deposited"]) / history_days / count, 3)
                if history_days and count
                else 0
            ),
        },
        "assumptions": {
            "daily_task_reward": DAILY_TASK_REWARD,
            "coins_per_lesson": COINS_PER_LESSON,
            "saturday_sessions": saturday_sessions,
            "sunday_sessions": sunday_sessions,
        },
        "rewards": reward_report,
    }
