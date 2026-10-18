
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.group import Group
    from app.models.user import User


class Teacher(Base):
    __tablename__ = "teachers"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user: Mapped["User"] = relationship(back_populates="teacher")
    groups_as_first_teacher: Mapped[list["Group"]] = relationship(
        back_populates="teacher_1",
        foreign_keys="Group.teacher_1_id",
        passive_deletes=True,
    )
    groups_as_second_teacher: Mapped[list["Group"]] = relationship(
        back_populates="teacher_2",
        foreign_keys="Group.teacher_2_id",
        passive_deletes=True,
    )
    