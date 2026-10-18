from enum import Enum, StrEnum

class StatusEnum(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    
class ProductMode(StrEnum):
    DEV = "DEV"
    PROD = "PROD"


class UserRole(StrEnum):
    STUDENT = "student"
    TEACHER = "teacher"


class CourseCategory(StrEnum):
    EMBEDDED = "embedded"
    GAME_DEV = "game dev"
    WEB = "web"
    PRIMARY = "primary"
    PYTHON = "python"
    NO_CATEGORY = "no category"

class BalanceChangeReasons(StrEnum):
    THEORY = "theory"
    PRACTICE_COMPLETED = "practice_completed"
    ADDITIONAL_TASK_COMPLETED = "additional_task_completed"
    DISCIPLINE_BREAKDOWN = "discipline_breakdown"
    MIDDLE_LEVEL_VIOLATION = "middle_level_violation"
    HARD_VIOLATION = "hard_violation"

    @property
    def balance_delta(self) -> int:
        return {
            BalanceChangeReasons.THEORY: 1,
            BalanceChangeReasons.PRACTICE_COMPLETED: 1,
            BalanceChangeReasons.ADDITIONAL_TASK_COMPLETED: 1,
            BalanceChangeReasons.DISCIPLINE_BREAKDOWN: -1,
            BalanceChangeReasons.MIDDLE_LEVEL_VIOLATION: -2,
            BalanceChangeReasons.HARD_VIOLATION: -3,
        }[self]
