from datetime import datetime
from typing import Literal

from core.enums import StatusEnum
from pydantic import BaseModel, ConfigDict, Field


class BalanceResponse(BaseModel):
    balance: int
    code: int = 200
    status: str = StatusEnum.SUCCESS


class BalanceChangeRequest(BaseModel):
    operation: Literal["deposit", "deduct"]
    amount: int = Field(gt=0)
    reason: str | None = None


class BalanceTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    operation: Literal["deposit", "deduct"]
    amount: int
    reason: str | None
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