from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from repositories.student import StudentRepository
from repositories.transaction import TransactionRepository
from schemas.balance import (
    BalanceChangeRequest,
    BalanceChangeResponse,
    BalanceHistoryResponse,
    BalanceResponse,
    BalanceTransactionResponse,
)
from services.balance import (
    BalanceService,
    InsufficientBalanceError,
    StudentNotFoundError,
    get_balance_service,
)

coins_router = APIRouter(prefix="/student", tags=["balance"])

#TODO: Added any auth and permission checks for each endpoint, if needed.

@coins_router.get("/{student_id}/balance", response_model=BalanceResponse)
async def get_student_balance_by_id(
    student_id: int,
    service: BalanceService = Depends(get_balance_service),
) -> BalanceResponse:
    try:
        balance = await service.get_balance(student_id)
    except StudentNotFoundError:
        raise HTTPException(status_code=404, detail="Student not found") from None
    return BalanceResponse(balance=balance)


@coins_router.post(
    "/{student_id}/balance/transactions",
    response_model=BalanceChangeResponse,
)
async def change_student_balance(
    student_id: int,
    change: BalanceChangeRequest,
    service: BalanceService = Depends(get_balance_service),
) -> BalanceChangeResponse:
    try:
        balance, transaction = await service.change_balance(student_id, change)
    except StudentNotFoundError:
        raise HTTPException(status_code=404, detail="Student not found") from None
    except InsufficientBalanceError:
        raise HTTPException(
            status_code=409,
            detail="Insufficient balance for this deduction",
        ) from None
    return BalanceChangeResponse(
        balance=balance,
        transaction=BalanceTransactionResponse.model_validate(transaction),
    )


@coins_router.get(
    "/{student_id}/transactions",
    response_model=BalanceHistoryResponse,
)
async def get_student_transaction_history(
    student_id: int,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: BalanceService = Depends(get_balance_service),
) -> BalanceHistoryResponse:
    try:
        transactions = await service.get_history(student_id, limit, offset)
    except StudentNotFoundError:
        raise HTTPException(status_code=404, detail="Student not found") from None
    return BalanceHistoryResponse(
        transactions=[
            BalanceTransactionResponse.model_validate(transaction)
            for transaction in transactions
        ]
    )