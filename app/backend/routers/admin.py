#backend/routers/admin.py
from typing_extensions import Annotated

from fastapi import Depends, APIRouter, Query
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession
from auth.dependencies import require_admin_token
from database import get_db
from models.user import UserResponse
from models.auth import RegisterRequest
from models.chat import ChatItem
from services.admin import get_all_users_service, delete_user_service, register_user_service, set_user_tokens_service, get_user_details_service, delete_chat_by_id, get_user_chats_service, mass_set_user_tokens_service
from models.user_token_balance import TokenUpdateRequest, TokenBalanceResponse, MassTokenUpdateResponse

router = APIRouter()

@router.get('/users', response_model=list[UserResponse])
async def get_users(
    skip: Annotated[int, Query(ge=0, description="Skip the first N users")] = 0,
    limit: Annotated[int, Query(ge=1, le=1000, description="Limit number of users returned")] = 100,
    db: AsyncSession = Depends(get_db), 
    _: str = Depends(require_admin_token)
) -> list[UserResponse]:
    users = await get_all_users_service(skip, limit, db)
    return users

@router.delete('/users/{user_id}', response_model=UserResponse)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), _: str = Depends(require_admin_token)) -> UserResponse:
    deleted_user = await delete_user_service(user_id, db)
    return deleted_user

@router.post('/users', response_model=UserResponse)
async def register_user(request: RegisterRequest, db: AsyncSession = Depends(get_db), _: str = Depends(require_admin_token)) -> UserResponse:
    result = await register_user_service(request.email, request.password, request.is_admin, db)
    return result

@router.patch('/users/{user_id}/tokens', response_model=TokenBalanceResponse)
async def update_user_token_balance(user_id: int, request: TokenUpdateRequest, db: AsyncSession = Depends(get_db), _: str = Depends(require_admin_token)) -> TokenBalanceResponse:
    updated_balance = await set_user_tokens_service(user_id, request.model_name, request.balance, db)
    return updated_balance

@router.patch('/users/tokens', response_model=MassTokenUpdateResponse)
async def update_multiple_user_token_balances(request: TokenUpdateRequest, db: AsyncSession = Depends(get_db), _: str = Depends(require_admin_token)) -> MassTokenUpdateResponse:
    updated_balances = await mass_set_user_tokens_service(request, db)
    return updated_balances


@router.get('/users/{user_id}', response_model=UserResponse)
async def get_user_details(
    user_id: int, 
    db: AsyncSession = Depends(get_db), 
    _: str = Depends(require_admin_token)
) -> UserResponse:
    user_data = await get_user_details_service(user_id, db)
    return UserResponse.model_validate(user_data)

@router.delete('/chat/{chat_id}', response_model=ChatItem)
async def delete_chat(chat_id: int, db: AsyncSession = Depends(get_db), _: str = Depends(require_admin_token)) -> ChatItem:
    deleted_chat = await delete_chat_by_id(chat_id, db)
    return deleted_chat

@router.get('/chats/{user_id}', response_model=list[ChatItem])
async def get_user_chats(user_id: int, db: AsyncSession = Depends(get_db), _: str = Depends(require_admin_token)) -> list[ChatItem]:
    chats = await get_user_chats_service(user_id, db)
    return chats