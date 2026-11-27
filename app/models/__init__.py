"""Import all ORM models so SQLAlchemy can resolve string relationships."""

from app.models.achievement import Achievement, StudentAchievement
from app.models.course import Course
from app.models.daily_task import CourseDailyTask, DailyTask, DailyTaskQuestion, StudentDailyTask
from app.models.google_oauth_state import GoogleOAuthState
from app.models.group import Group
from app.models.reward import Reward
from app.models.session import Session
from app.models.streak import Streak
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.telegram_link_token import TelegramLinkToken
from app.models.transaction import BalanceTransaction
from app.models.user import User

__all__ = [
    "Achievement",
    "BalanceTransaction",
    "Course",
    "CourseDailyTask",
    "DailyTask",
    "DailyTaskQuestion",
    "GoogleOAuthState",
    "Group",
    "Reward",
    "Session",
    "Streak",
    "Student",
    "StudentAchievement",
    "StudentDailyTask",
    "Teacher",
    "TelegramLinkToken",
    "User",
]
