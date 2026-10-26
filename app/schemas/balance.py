from datetime import datetime
from typing import Literal

from app.schemas.base import APIResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.core.enums import BalanceChangeReasons, BalanceChangeType


class BalanceResponse(APIResponse):
    balance: float


class BalanceChangeRequest(BaseModel):
    reason: list[BalanceChangeReasons] = Field(min_length=1)

    @field_validator("reason")
    @classmethod
    def reasons_must_be_unique(
        cls,
        reasons: list[BalanceChangeReasons],
    ) -> list[BalanceChangeReasons]:
        if len(reasons) != len(set(reasons)):
            raise ValueError("Reasons must be unique")
        return reasons

    @model_validator(mode="after")
    def reasons_must_change_balance(self) -> "BalanceChangeRequest":
        if sum(reason.balance_delta for reason in self.reason) == 0:
            raise ValueError("Selected reasons must change the balance")
        return self


class BalanceTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    operation: Literal["deposit", "deduct"]
    amount: float
    reason: list[str] | None
    cancelled_at: datetime | None = None
    cancelled_by_user_id: int | None = None
    created_at: datetime


class BalanceChangeResponse(APIResponse):
    balance: float
    transaction: BalanceTransactionResponse


class BalanceHistoryResponse(APIResponse):
    transactions: list[BalanceTransactionResponse]


class GroupPracticeAwardStudent(BaseModel):
    student_id: int
    balance: float
    transaction: BalanceTransactionResponse


class GroupPracticeAwardResponse(APIResponse):
    group_id: int
    affected_students: int
    students: list[GroupPracticeAwardStudent]


class BalanceChangeReasonItem(BaseModel):
    reason: BalanceChangeReasons
    type: BalanceChangeType


class BalanceChangeReasonsResponse(APIResponse):
    reasons: list[BalanceChangeReasonItem]
