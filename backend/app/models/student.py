from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base

class Student(Base):
    __tablename__ = "students"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    group: Mapped[str] = mapped_column(String, nullable=False)
    avatar: Mapped[str] = mapped_column(String, nullable=True)
    balance: Mapped[int] = mapped_column(Integer, default=0)
    hash_access_key: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    
    # TODO: Add achievements, transactions, and other relevant fields as needed