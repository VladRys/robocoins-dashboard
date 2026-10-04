from typing import List

from sqlalchemy import String, Column, Integer
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.core.database import Base

class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True))
    name: Mapped[str]

    groups: Mapped[List["Group"]] = relationship(back_populates="course")
