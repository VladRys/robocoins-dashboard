from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.reward import RewardProgressResponse, RewardResponse
from app.services import authorization
from app.services.authorization import AuthorizationService
from app.services.reward import RewardService
from app.services.student import StudentService

from app.api.dependencies import (
    get_authenticated_teacher,
    get_authenticated_user,
    get_authorization_service,
    get_balance_service,
    get_reward_service,
    get_student_service,
)
from app.core.enums import AuthorizationAction, HttpErrorMessage, BalanceChangeReasons
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
    student_service: StudentService = Depends(get_student_service),
    rewards_service: RewardService = Depends(get_reward_service),
    _user: User = Depends(get_authenticated_user),
) -> RewardProgressResponse:
    student = await student_service.get_student_by_id(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=HttpErrorMessage.STUDENT_NOT_FOUND)

    progress = await rewards_service.get_student_reward_progress(
        student_id=student_id,
        balance=student.balance,
        current_goal=student.current_goal,
    )
    return RewardProgressResponse(
        balance=student.balance,
        current_goal=(
            RewardResponse.model_validate(progress.current_goal)
            if progress.current_goal is not None
            else None
        ),
        coins_remaining=progress.coins_remaining,
        progress_percent=progress.progress_percent,
    )


@coins_router.post(
    "/{student_id}/balance/transactions",
    response_model=BalanceChangeResponse,
)
async def change_student_balance(
    student_id: int,
    change: BalanceChangeRequest,
    service: BalanceService = Depends(get_balance_service),
    authorization: AuthorizationService = Depends(get_authorization_service),
    _user: User = Depends(get_authenticated_user),
) -> BalanceChangeResponse:
    try:
        if not await authorization.is_allowed(AuthorizationAction.TEACHER_AND_ADMIN_OPERATION, _user, subject_id=student_id):
            raise HTTPException(status_code=403, detail=HttpErrorMessage.FORBIDDEN) from None
        
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
    _user: User = Depends(get_authenticated_user),
    authorization: AuthorizationService = Depends(get_authorization_service),
) -> BalanceChangeResponse:
    try:
        if not await authorization.is_allowed(AuthorizationAction.TEACHER_AND_ADMIN_OPERATION, _user):
            raise HTTPException(status_code=403, detail=HttpErrorMessage.FORBIDDEN) from None
        
        balance, transaction = await service.cancel_transaction(
            transaction_id,
            cancelled_by_user_id=_user.id,
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
