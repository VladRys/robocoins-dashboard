from sqlalchemy import CheckConstraint, Enum as SqlEnum, ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column, Mapped

from app.core.database import Base
from app.core.enums import RewardType

class Reward(Base):
    __tablename__ = "rewards"
    __table_args__ = (
        CheckConstraint(
            "(type = 'privilege' AND course_id IS NULL) OR "
            "(type = 'reward' AND course_id IS NOT NULL)",
            name="ck_rewards_type_course",
        ),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    type: Mapped[RewardType] = mapped_column(
        SqlEnum(
            RewardType,
            name="reward_type",
            native_enum=False,
            create_constraint=True,
            values_callable=lambda types: [reward_type.value for reward_type in types],
        ),
        nullable=False,
        default=RewardType.REWARD,
    )
    course_id: Mapped[int | None] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=True
    )
    # TODO: mb add server-side icon
    # TODO: also add unique rewards depends on course
