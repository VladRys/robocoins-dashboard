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
    GROUPS_NOT_FOUND = "One or more groups were not found"
    GROUP_HAS_TOO_MANY_TEACHERS = "A group can have at most two teachers"
    DUPLICATE_TEACHER_IDS = "Teacher IDs must be unique"
    TEACHERS_NOT_FOUND = "One or more teachers were not found"
    INVALID_TEACHER_ASSIGNMENT = "Invalid teacher assignment"
    COURSE_ALREADY_EXISTS = "A course with this name already exists"
    COURSE_CREATION_FAILED = "Course creation failed"


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

class BalanceChangeType(StrEnum):
    PUNISH = "punish"
    REWARD = "reward"


class BalanceChangeReasons(StrEnum):
    THEORY = "theory"
    PRACTICE_COMPLETED = "practice_completed"
    ADDITIONAL_TASK_COMPLETED = "additional_task_completed"
    DISCIPLINE_BREAKDOWN = "discipline_breakdown"
    MIDDLE_LEVEL_VIOLATION = "middle_level_violation"
    SERIOUS_VIOLATION = "serious_violation"

    @property
    def type(self) -> BalanceChangeType:
        return {
            BalanceChangeReasons.THEORY: BalanceChangeType.REWARD,
            BalanceChangeReasons.PRACTICE_COMPLETED: BalanceChangeType.REWARD,
            BalanceChangeReasons.ADDITIONAL_TASK_COMPLETED: BalanceChangeType.REWARD,
            BalanceChangeReasons.DISCIPLINE_BREAKDOWN: BalanceChangeType.PUNISH,
            BalanceChangeReasons.MIDDLE_LEVEL_VIOLATION: BalanceChangeType.PUNISH,
            BalanceChangeReasons.SERIOUS_VIOLATION: BalanceChangeType.PUNISH,
        }[self]

    @property
    def balance_delta(self) -> int:
        return {
            BalanceChangeReasons.THEORY: 1,
            BalanceChangeReasons.PRACTICE_COMPLETED: 1,
            BalanceChangeReasons.ADDITIONAL_TASK_COMPLETED: 1,
            BalanceChangeReasons.DISCIPLINE_BREAKDOWN: -1,
            BalanceChangeReasons.MIDDLE_LEVEL_VIOLATION: -2,
            BalanceChangeReasons.SERIOUS_VIOLATION: -3,
        }[self]
