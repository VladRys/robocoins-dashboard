from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.reward import RewardProgressResponse, RewardResponse
from app.services.reward import RewardService

from app.api.dependencies import (
    get_authenticated_teacher,
    get_authenticated_user,
    get_balance_service,
    get_reward_service,
)
from app.core.enums import HttpErrorMessage, BalanceChangeReasons
from app.models.user import User
from app.schemas.balance import (
    BalanceChangeRequest,
    BalanceChangeResponse,
    BalanceHistoryResponse,
    BalanceResponse,
    BalanceTransactionResponse,
    BalanceChangeReasonsResponse
)
from app.services.balance import (
    BalanceService,
    InsufficientBalanceToCancelError,
    StudentNotFoundError,
    TransactionAlreadyCancelledError,
    TransactionNotFoundError,
)

coins_router = APIRouter(prefix="/student", tags=["balance"])
coins_ext_router = APIRouter(prefix="/ext/balance", tags=["balance"])


@coins_router.get("/{student_id}/balance", response_model=BalanceResponse)
async def get_student_balance_by_id(
    student_id: int,
    service: BalanceService = Depends(get_balance_service),
    _user: User = Depends(get_authenticated_user),
) -> BalanceResponse:
    try:
        balance = await service.get_balance(student_id)
    except StudentNotFoundError:
        raise HTTPException(status_code=404, detail=HttpErrorMessage.STUDENT_NOT_FOUND) from None
    return BalanceResponse(balance=balance)


@coins_router.get("/{student_id}/reward-progress", response_model=RewardProgressResponse)
async def get_student_reward_progress(
    student_id: int,
    service: BalanceService = Depends(get_balance_service),
    rewards_service: RewardService = Depends(get_reward_service),
    _user: User = Depends(get_authenticated_user),
) -> RewardProgressResponse:
    try:
        balance = await service.get_balance(student_id)
    except StudentNotFoundError:
        raise HTTPException(status_code=404, detail=HttpErrorMessage.STUDENT_NOT_FOUND) from None

    next_reward = next(
        (reward for reward in await rewards_service.get_rewards_for_student(student_id) if reward.price > balance),
        None,
    )
    if next_reward is None:
        return RewardProgressResponse(
            balance=balance,
            reward=None,
            coins_remaining=None,
            progress_percent=None,
        )

    return RewardProgressResponse(
        balance=balance,
        reward=RewardResponse.model_validate(next_reward),
        coins_remaining=next_reward.price - balance,
        progress_percent=round(balance / next_reward.price * 100, 2),
    )


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
        raise HTTPException(status_code=404, detail=HttpErrorMessage.STUDENT_NOT_FOUND) from None
    return BalanceChangeResponse(
        balance=balance,
        transaction=BalanceTransactionResponse.model_validate(transaction),
    )


@coins_router.post(
    "/transactions/{transaction_id}/cancel",
    response_model=BalanceChangeResponse,
)
async def cancel_student_transaction(
    transaction_id: int,
    service: BalanceService = Depends(get_balance_service),
    teacher: User = Depends(get_authenticated_teacher),
) -> BalanceChangeResponse:
    try:
        balance, transaction = await service.cancel_transaction(
            transaction_id,
            cancelled_by_user_id=teacher.id,
        )
    except TransactionNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=HttpErrorMessage.TRANSACTION_NOT_FOUND,
        ) from None
    except TransactionAlreadyCancelledError:
        raise HTTPException(
            status_code=409,
            detail=HttpErrorMessage.TRANSACTION_ALREADY_CANCELLED,
        ) from None
    except InsufficientBalanceToCancelError:
        raise HTTPException(
            status_code=409,
            detail=HttpErrorMessage.INSUFFICIENT_BALANCE_TO_CANCEL_TRANSACTION,
        ) from None

    return BalanceChangeResponse(
        balance=balance,
        transaction=BalanceTransactionResponse.model_validate(transaction),
    )

@coins_ext_router.get("/balanceChangeReasons")
async def get_balance_change_reasons(
    _user: User = Depends(get_authenticated_user),
) -> BalanceChangeReasonsResponse:
    return BalanceChangeReasonsResponse(
        reasons=[{"reason": reason, "type": reason.type} for reason in BalanceChangeReasons],
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
        raise HTTPException(status_code=404, detail=HttpErrorMessage.STUDENT_NOT_FOUND) from None
    return BalanceHistoryResponse(
        transactions=[
            BalanceTransactionResponse.model_validate(transaction)
            for transaction in transactions
        ]
    )
