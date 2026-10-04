from sqlalchemy import ForeignKey, String, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] # Name example: СБ 16:00
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    course: Mapped["Course"] = relationship(back_populates="groups")
    students: Mapped[list["Student"]] = relationship(back_populates="group")
