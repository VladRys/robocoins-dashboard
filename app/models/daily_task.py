from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum as SqlEnum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import Config
from app.core.database import Base
from app.core.enums import TaskType

if TYPE_CHECKING:
    from app.models.student import Student


class DailyTaskQuestion(Base):
    __tablename__ = "daily_task_questions"
    __table_args__ = (
        CheckConstraint("reward > 0", name="ck_daily_task_questions_reward_positive"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    question: Mapped[str] = mapped_column(String, nullable=False)
    task_type: Mapped[TaskType] = mapped_column(
        SqlEnum(
            TaskType,
            name="daily_task_type",
            native_enum=False,
            create_constraint=True,
            values_callable=lambda types: [task_type.value for task_type in types],
        ),
        nullable=False,
    )
    options: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    course_ids: Mapped[list[int]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    answer: Mapped[str] = mapped_column(String(200), nullable=False)
    reward: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=Config.DAILY_TASK_REWARD,
    )
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)
    hotspots: Mapped[list[dict[str, int | str]] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    daily_task: Mapped["DailyTask"] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        single_parent=True,
    )


class DailyTask(Base):
    __tablename__ = "daily_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("daily_task_questions.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )
    last_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    question: Mapped[DailyTaskQuestion] = relationship(back_populates="daily_task")
    student_assignments: Mapped[list["StudentDailyTask"]] = relationship(
        back_populates="daily_task",
    )


class StudentDailyTask(Base):
    __tablename__ = "student_daily_tasks"
    __table_args__ = (
        UniqueConstraint("student_id", "task_date", name="uq_student_daily_task_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    daily_task_id: Mapped[int] = mapped_column(
        ForeignKey("daily_tasks.id", ondelete="RESTRICT"),
        nullable=False,
    )
    task_date: Mapped[date] = mapped_column(Date, nullable=False)
    submitted_answer: Mapped[str | None] = mapped_column(String(200), nullable=True)
    correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    student: Mapped["Student"] = relationship()
    daily_task: Mapped[DailyTask] = relationship(back_populates="student_assignments")
