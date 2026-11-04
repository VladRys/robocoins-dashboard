from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.group import Group
    from app.models.transaction import BalanceTransaction
    from app.models.user import User
    from app.models.streak import Streak


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
    avatar: Mapped[str | None] = mapped_column(String, nullable=True)
    balance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    hash_access_key: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    # Access code - keyword for auth.
    access_code: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    # TODO: Add achievements and streak system
    current_streak: Mapped[list["Streak"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
