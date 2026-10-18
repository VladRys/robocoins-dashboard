from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import get_authenticated_teacher, get_authenticated_user
from models.user import User
from schemas.balance import (
    BalanceChangeRequest,
    BalanceChangeResponse,
    BalanceHistoryResponse,
    BalanceResponse,
    BalanceTransactionResponse,
)
from services.balance import (
    BalanceService,
    StudentNotFoundError,
    get_balance_service,
)

coins_router = APIRouter(prefix="/student", tags=["balance"])

# TODO: Do server-side validation for some type of actions, add just single endpoint with reason and action type (reward, punish)


@coins_router.get("/{student_id}/balance", response_model=BalanceResponse)
async def get_student_balance_by_id(
    student_id: int,
    service: BalanceService = Depends(get_balance_service),
    _user: User = Depends(get_authenticated_user),
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
    _user: User = Depends(get_authenticated_teacher),
) -> BalanceChangeResponse:
    try:
        balance, transaction = await service.change_balance(student_id, change)
    except StudentNotFoundError:
        raise HTTPException(status_code=404, detail="Student not found") from None
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
    user: User = Depends(get_authenticated_user),
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
