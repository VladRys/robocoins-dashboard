from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.group import Group
    from app.models.student import Student


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (UniqueConstraint("name", name="uq_courses_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    groups: Mapped[list["Group"]] = relationship(back_populates="course")
    students: Mapped[list["Student"]] = relationship(
        back_populates="course",
        viewonly=True,
    )
