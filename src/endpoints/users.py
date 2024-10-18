from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository.users import db_user_repo
from src.schemas.users import UserResponse, UserRequest
from src.services.auth import password_manager

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
        body: UserRequest,
        db: AsyncSession = Depends(get_db),
) -> UserResponse:
    existent_user = await db_user_repo.get_user_by_email(body.email, db)
    if existent_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    body.password = password_manager.get_password_hash(body.password)
    new_user = await db_user_repo.create_user(body, db)
    # background_tasks.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user