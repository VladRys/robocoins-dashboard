from sqlalchemy import CheckConstraint, Enum as SqlEnum, Integer, String
from sqlalchemy.orm import mapped_column, Mapped

from app.core.database import Base
from app.core.enums import CourseCategory, RewardType

class Reward(Base):
    __tablename__ = "rewards"
    __table_args__ = (
        CheckConstraint(
            "(type = 'privilege' AND course_category IS NULL) OR type = 'reward'",
            name="ck_rewards_type_course_category",
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
    course_category: Mapped[CourseCategory | None] = mapped_column(
        SqlEnum(
            CourseCategory,
            name="reward_course_category",
            native_enum=False,
            create_constraint=True,
            values_callable=lambda categories: [category.value for category in categories],
        ),
        nullable=True,
    )
    # TODO: mb add server-side icon
    # TODO: also add unique rewards depends on course
