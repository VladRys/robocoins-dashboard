from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.teacher import Teacher


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('student', 'teacher')",
            name="ck_users_role",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    access_code: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    student: Mapped["Student | None"] = relationship(
        back_populates="user",
        foreign_keys="Student.user_id",
        uselist=False,
        passive_deletes=True,
    )
    teacher: Mapped["Teacher | None"] = relationship(
        back_populates="user",
        uselist=False,
        passive_deletes=True,
    )
