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
