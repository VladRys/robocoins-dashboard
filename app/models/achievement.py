from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Enum as SqlEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import AchievementType

if TYPE_CHECKING:
    from app.models.student import Student


class Achievement(Base):
    __tablename__ = "achievements"
    __table_args__ = (
        CheckConstraint(
            "required_coins IS NULL OR required_coins > 0",
            name="ck_achievements_required_coins_positive",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    icon: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[AchievementType] = mapped_column(
        SqlEnum(
            AchievementType,
            name="achievement_type",
            native_enum=False,
            create_constraint=True,
            values_callable=lambda types: [achievement_type.value for achievement_type in types],
        ),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(String, nullable=False)
    required_coins: Mapped[int | None] = mapped_column(Integer, nullable=True)

    students: Mapped[list[StudentAchievement]] = relationship(
        back_populates="achievement",
        cascade="all, delete-orphan",
    )

class StudentAchievement(Base):
    __tablename__ = "student_achievements"

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        primary_key=True,
    )
    achievement_id: Mapped[int] = mapped_column(
        ForeignKey("achievements.id", ondelete="CASCADE"),
        primary_key=True,
    )

    student: Mapped[Student] = relationship(back_populates="achievements")
    achievement: Mapped[Achievement] = relationship(back_populates="students")