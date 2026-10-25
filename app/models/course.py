from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum as SqlEnum, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import CourseCategory

if TYPE_CHECKING:
    from app.models.group import Group


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (UniqueConstraint("name", name="uq_courses_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[CourseCategory] = mapped_column(
        SqlEnum(
            CourseCategory,
            name="course_category",
            native_enum=False,
            create_constraint=True,
            values_callable=lambda categories: [category.value for category in categories],
        ),
        nullable=False,
        default=CourseCategory.NO_CATEGORY.value,
        server_default=CourseCategory.NO_CATEGORY.value
    )

    groups: Mapped[list["Group"]] = relationship(back_populates="course")
