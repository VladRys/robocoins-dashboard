from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.student import Student
    from app.models.teacher import Teacher

student_groups = Table(
    "student_groups",
    Base.metadata,
    Column("student_id", ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
    Column("group_id", ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
)


class Group(Base):
    __tablename__ = "groups"
    __table_args__ = (
        CheckConstraint(
            "teacher_1_id IS NULL OR teacher_1_id != teacher_2_id",
            name="ck_groups_distinct_teachers",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    teacher_1_id: Mapped[int | None] = mapped_column(
        ForeignKey("teachers.user_id", ondelete="SET NULL"),
        nullable=True,
    )
    teacher_2_id: Mapped[int | None] = mapped_column(
        ForeignKey("teachers.user_id", ondelete="SET NULL"),
        nullable=True,
    )
    course: Mapped["Course"] = relationship(back_populates="groups")
    students: Mapped[list["Student"]] = relationship(
        secondary=student_groups,
        back_populates="groups",
    )
    teacher_1: Mapped["Teacher | None"] = relationship(
        back_populates="groups_as_first_teacher",
        foreign_keys=[teacher_1_id],
    )
    teacher_2: Mapped["Teacher | None"] = relationship(
        back_populates="groups_as_second_teacher",
        foreign_keys=[teacher_2_id],
    )
