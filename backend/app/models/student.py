from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.group import Group
    from app.models.course import Course
    from app.models.transaction import BalanceTransaction
    from app.models.user import User


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_students_user_id"),
        CheckConstraint("id = user_id", name="ck_students_id_matches_user_id"),
    )

    id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    user: Mapped["User"] = relationship(
        back_populates="student",
        foreign_keys=[user_id],
    )

    groups: Mapped[list["Group"]] = relationship(
        secondary="student_groups",
        back_populates="students",
    )
    transactions: Mapped[list["BalanceTransaction"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
    )
    course_name: Mapped[str] = mapped_column(ForeignKey("courses.name"), nullable=False)
    course: Mapped["Course"] = relationship(back_populates="students", viewonly=True)
    avatar: Mapped[str | None] = mapped_column(String, nullable=True)
    balance: Mapped[int] = mapped_column(Integer, default=0)
    hash_access_key: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    # Access code - keyword for auth.
    access_code: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    # TODO: Add achievements and other relevant fields as needed
