from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column, Mapped

from app.core.database import Base

class Reward(Base):
    __tablename__ = "rewards"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    # TODO: mb add server-side icon
    # TODO: also add unique rewards depends on course
