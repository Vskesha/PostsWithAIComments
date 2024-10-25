from typing import List

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import messages
from src.database.db import get_db
from src.database.models import User
from src.repository.users import user_repo
from src.schemas.email import MessageSchema
from src.schemas.users import UserResponse, ChangeRoleModel, AnswerDelayModel
from src.services.auth import auth_service
from src.services.roles_access import admin_moderator_access, admin_access

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", description="get logged user's info", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(auth_service.get_current_user),
) -> User:
    return current_user


@router.get(
    "/all",
    description="for admins and moderators only",
    response_model=List[UserResponse],
    dependencies=[Depends(admin_moderator_access)],
)
async def get_all_users(
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> List[User]:
    users = await user_repo.get_users(limit, offset, db)
    return users


@router.get(
    "/{user_id}",
    description="for admins and moderators only",
    response_model=UserResponse,
    dependencies=[Depends(admin_moderator_access)],
)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await user_repo.get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND
        )
    return user


@router.patch(
    "/ban/{user_id}",
    description="for admins and moderators only",
    response_model=MessageSchema,
    dependencies=[Depends(admin_moderator_access)],
)
async def ban_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> MessageSchema:
    user = await user_repo.get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND
        )
    await user_repo.ban_user(user_id, db)
    return MessageSchema(message=messages.USER_WAS_BANNED)


@router.patch(
    "/unban/{user_id}",
    description="for admins and moderators only",
    response_model=MessageSchema,
    dependencies=[Depends(admin_moderator_access)],
)
async def ban_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> MessageSchema:
    user = await user_repo.get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND
        )
    await user_repo.unban_user(user_id, db)
    return MessageSchema(message=messages.USER_WAS_UNBANNED)


@router.patch(
    "/change_role",
    description="for admins only",
    response_model=MessageSchema,
    dependencies=[Depends(admin_access)],
)
async def change_role(
    body: ChangeRoleModel,
    db: AsyncSession = Depends(get_db),
) -> MessageSchema:
    user = await user_repo.get_user_by_id(body.user_id, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND
        )
    await user_repo.change_role(body, db)
    return MessageSchema(message=messages.ROLE_WAS_CHANGED)


@router.patch(
    "/answer_delay",
    response_model=MessageSchema,
)
async def answer_delay(
    body: AnswerDelayModel,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageSchema:
    """
    The answer_delay function sets the auto answer delay for a user.
    To switch off auto answer - set to null
    :param body: AnswerDelayModel: data to change
    :param current_user: User: current logged in user
    :param db: AsyncSession: connection to database
    :return: MessageSchema: message if answer delay was changed
    """
    await user_repo.set_answer_delay(current_user.id, body.delay, db)
    return MessageSchema(message=messages.ANSWER_DELAY_WAS_SET)
