from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.group import Group


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    group: Mapped["Group"] = relationship(back_populates="students")
    course_name: Mapped[str] = mapped_column(ForeignKey("courses.name"), nullable=False)
    avatar: Mapped[str | None] = mapped_column(String, nullable=True)
    balance: Mapped[int] = mapped_column(Integer, default=0)
    hash_access_key: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    # Access code - keyword for auth.
    access_code: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    # TODO: Add achievements, transactions, and other relevant fields as needed
