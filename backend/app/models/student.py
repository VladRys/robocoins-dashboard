from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.group import Group
    from app.models.course import Course
    from app.models.transaction import BalanceTransaction


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    group: Mapped["Group"] = relationship(back_populates="students")
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
