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