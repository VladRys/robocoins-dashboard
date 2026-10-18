from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.core.enums import UserRole
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
from services.session import SessionService, get_session_service
from services.users import UserService, get_user_service

coins_router = APIRouter(prefix="/student", tags=["balance"])

# TODO: Do server-side validation for some type of actions, add just single endpoint with reason and action type (reward, punish)


async def _get_authenticated_user(
    request: Request,
    session_service: SessionService,
    user_service: UserService,
) -> User:
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session = await session_service.get_session_by_token(token)
    if session is None:
        raise HTTPException(status_code=401, detail="Invalid session token")
    if session.is_expired():
        await session_service.delete_session(token)
        raise HTTPException(status_code=401, detail="Session expired")

    user = await user_service.get_user_by_id(session.user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

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
    request: Request,
    service: BalanceService = Depends(get_balance_service),
    session_service: SessionService = Depends(get_session_service),
    user_service: UserService = Depends(get_user_service),
) -> BalanceChangeResponse:
    user = await _get_authenticated_user(request, session_service, user_service)
    if user.role != UserRole.TEACHER.value:
        raise HTTPException(
            status_code=403,
            detail="Only teachers can change student balances",
        )

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
    request: Request,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: BalanceService = Depends(get_balance_service),
    session_service: SessionService = Depends(get_session_service),
    user_service: UserService = Depends(get_user_service),
) -> BalanceHistoryResponse:
    user = await _get_authenticated_user(request, session_service, user_service)
    is_teacher = user.role == UserRole.TEACHER.value
    is_student_owner = (
        user.role == UserRole.STUDENT.value
        and user.id == student_id
    )
    if not is_teacher and not is_student_owner:
        raise HTTPException(
            status_code=403,
            detail="Only teachers and the student can view this transaction history",
        )

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
