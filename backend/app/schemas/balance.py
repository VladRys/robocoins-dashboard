from datetime import datetime
from typing import Literal

from core.enums import StatusEnum
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.core.enums import BalanceChangeReasons, BalanceChangeType


class BalanceResponse(BaseModel):
    balance: int
    code: int = 200
    status: str = StatusEnum.SUCCESS


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
    amount: int
    reason: list[str] | None
    created_at: datetime


class BalanceChangeResponse(BaseModel):
    balance: int
    transaction: BalanceTransactionResponse
    code: int = 200
    status: str = StatusEnum.SUCCESS


class BalanceHistoryResponse(BaseModel):
    transactions: list[BalanceTransactionResponse]
    code: int = 200
    status: str = StatusEnum.SUCCESS


class BalanceChangeReasonItem(BaseModel):
    reason: BalanceChangeReasons
    type: BalanceChangeType


class BalanceChangeReasonsResponse(BaseModel):
    code: int = 200
    status: str = StatusEnum.SUCCESS
    reasons: list[BalanceChangeReasonItem]
