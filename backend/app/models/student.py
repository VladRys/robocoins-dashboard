from sqlalchemy import Column, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    # TODO: refactor model for many groups for single student.
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))
    group: Mapped["Group"] = relationship(back_populates="students", nullable = False)
    course: Mapped[str] = mapped_column(String, nullable=False)
    avatar: Mapped[str] = mapped_column(String, nullable=True)
    balance: Mapped[int] = mapped_column(Integer, default=0)
    hash_access_key: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    # Access code - keyword for auth.
    access_code: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    # TODO: Add achievements, transactions, and other relevant fields as needed
