from enum import Enum, StrEnum


class HttpErrorMessage(str, Enum):
    NOT_AUTHENTICATED = "Not authenticated"
    INVALID_SESSION_TOKEN = "Invalid session token"
    INVALID_SESSION = "Invalid session"
    SESSION_EXPIRED = "Session expired"
    USER_NOT_FOUND = "User not found"
    WRONG_ACCESS_CODE = "Wrong access code"
    STUDENT_PROFILE_NOT_FOUND = "Student profile not found"
    STUDENT_NOT_FOUND = "Student not found"
    TEACHER_NOT_FOUND = "Teacher not found"
    TEACHER_PROFILE_NOT_FOUND = "Teacher profile not found"
    GROUP_NOT_FOUND = "Group not found"
    FAILED_TO_CREATE_TEACHER = "Failed to create teacher"
    FAILED_TO_CREATE_GROUP = "Failed to create group"
    FAILED_TO_CREATE_STUDENT = "Failed to create student"
    UNSUPPORTED_USER_ROLE = "Unsupported user role"
    ONLY_TEACHERS_CAN_MODIFY = "Only teachers can modify this resource"


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
