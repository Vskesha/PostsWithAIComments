from fastapi import APIRouter, status, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import messages
from src.database.db import get_db
from src.repository.users import db_user_repo
from src.schemas.tokens import TokenSchema
from src.schemas.users import UserResponse, UserRequest
from src.services.auth import password_manager, auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    The signup function creates a new user in the database.
        It takes in the body (which is a UserRequest), and db as parameters.
        If an account with the same email already exists, it raises an
        HTTPException with status code 409 and detail Account already exists.
        Otherwise, it hashes the password using the password_manager, creates
        a new user using the db_user_repo, and sends an email to the user's email address.

    :param body: UserRequest: data for sihning up
    :param db: AsyncSession: connetion to the database
    :return: UserResponse: newly created user
    """
    existent_user = await db_user_repo.get_user_by_email(body.email, db)
    if existent_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_ALREADY_EXISTS
        )
    body.password = password_manager.get_password_hash(body.password)
    new_user = await db_user_repo.create_user(body, db)
    # background_tasks.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model=TokenSchema)
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    The login function authenticates a user.
        It takes the username and password from the request body,
        verifies that they are correct, and returns an access and refresh token.
    :param body: OAuth2PasswordRequestForm: the request body
    :param db: AsyncSession: database session
    :return: TokenResponse: access and refresh token
    """
    user = await db_user_repo.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_EMAIL
        )
    # if not user.email_confirmed:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.EMAIL_NOT_CONFIRMED)
    if not password_manager.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_PASSWORD
        )
    if not user.status_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.USER_IS_BANNED
        )
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await db_user_repo.update_refresh_token(user.email, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/refresh_token")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(),
    db: AsyncSession = Depends(get_db),
):
    return {}
