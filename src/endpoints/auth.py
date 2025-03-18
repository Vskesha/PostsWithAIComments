from random import randint

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Request,
    Security,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordRequestForm,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import messages
from src.database.db import get_db
from src.database.models import User
from src.repository.tokens import token_repo
from src.repository.users import user_repo
from src.schemas.email import EmailSchema, MessageSchema
from src.schemas.tokens import TokenData, TokenSchema
from src.schemas.users import ChangePasswordSchema, UserRequest, UserResponse
from src.services.auth import auth_service, password_manager, token_manager
from src.services.email import email_service

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    The signup function creates a new user in the database.
        It takes in the body (which is a UserRequest), and db as parameters.
        If an account with the same email already exists, it raises an
        HTTPException with status code 409 and detail Account already exists.
        Otherwise, it hashes the password using the password_manager, creates
        a new user using the user_repo, and sends an email to the user's email address.

    :param body: UserRequest: data for sihning up
    :param background_tasks: BackgroundTasks: add a task to the background queue
    :param request: Request: request object
    :param db: AsyncSession: connetion to the database
    :return: UserResponse: newly created user
    """
    existent_user = await user_repo.get_user_by_email(body.email, db)
    if existent_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_ALREADY_EXISTS
        )
    body.password = password_manager.get_password_hash(body.password)
    new_user = await user_repo.create_user(body, db)
    background_tasks.add_task(
        email_service.send_verification_email,
        new_user,
        request.base_url,
    )
    return new_user


async def create_access_and_refresh_tokens(
    user: User,
    db: AsyncSession,
) -> TokenSchema:
    access_token = await token_manager.create_access_token(data={"sub": user.email})
    refresh_token = await token_manager.create_refresh_token(data={"sub": user.email})

    access_token_data = TokenData(
        token=access_token,
        expires=await token_manager.get_expire_date(access_token),
        blocked=False,
        user_id=user.id,
    )
    refresh_token_data = TokenData(
        token=refresh_token,
        expires=await token_manager.get_expire_date(refresh_token),
        blocked=False,
        user_id=user.id,
    )
    await token_repo.add_token(access_token_data, db)
    await token_repo.add_token(refresh_token_data, db)

    return TokenSchema(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/login", response_model=TokenSchema)
async def login(
    background_tasks: BackgroundTasks,
    body: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenSchema:
    """
    The login function authenticates a user.
        It takes the username and password from the request body,
        verifies that they are correct, and returns an access and refresh token.
    :param body: OAuth2PasswordRequestForm: the request body
    :param db: AsyncSession: database session
    :return: TokenResponse: access and refresh token
    """
    user = await user_repo.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_EMAIL
        )
    if not user.email_confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.EMAIL_NOT_CONFIRMED,
        )
    if not password_manager.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_PASSWORD
        )
    if user.banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.USER_WAS_BANNED
        )

    # delete old expired tokens if one of ten cases
    # TODO: scedule this in some type of queue
    if randint(1, 10) == 1:
        background_tasks.add_task(token_repo.delete_expired, db)

    return await create_access_and_refresh_tokens(user, db)


@router.get("/refresh_token", response_model=TokenSchema)
async def refresh_token(
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db),
) -> TokenSchema:
    token = credentials.credentials
    db_token = await token_repo.get_token(token, db)
    user_email = await token_manager.decode_refresh_token(token)
    user = await user_repo.get_user_by_email(user_email, db)

    if not db_token or db_token.blocked or db_token.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.INVALID_REFRESH_TOKEN,
        )

    await token_repo.block_token(token, db)

    # delete old expired tokens if one of ten cases
    # TODO: scedule this in some type of queue
    if randint(1, 10) == 1:
        background_tasks.add_task(token_repo.delete_expired, db)

    return await create_access_and_refresh_tokens(user, db)


@router.get("/confirmed_email/{token}", response_model=MessageSchema)
async def confirmed_email(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> MessageSchema:
    email = await token_manager.get_email_from_token(token)
    user = await user_repo.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=messages.VERIFICATION_ERROR,
        )
    await user_repo.confirm_email(email, db)
    return MessageSchema(message=messages.EMAIL_CONFIRMED)


@router.post("/resend_confirmation", response_model=MessageSchema)
async def resend_confirmation_email(
    body: EmailSchema,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> MessageSchema:
    user = await user_repo.get_user_by_email(body.email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND
        )
    if user.email_confirmed:
        return MessageSchema(message=messages.EMAIL_CONFIRMED)
    background_tasks.add_task(
        email_service.send_verification_email,
        user,
        request.base_url,
    )
    return MessageSchema(message="Check your email for confirmation.")


@router.get("/logout", response_model=MessageSchema)
async def logout(
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageSchema:
    await token_repo.block_user_tokens(current_user.id, db)
    return MessageSchema(message="Logged out")


@router.post("/change_password", response_model=MessageSchema)
async def change_password(
    body: ChangePasswordSchema,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageSchema:
    if not password_manager.verify_password(body.old_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_PASSWORD
        )
    new_password_hash = password_manager.get_password_hash(body.new_password)
    await user_repo.update_password(current_user.id, new_password_hash, db)
    return MessageSchema(message=messages.PASSWORD_CHANGED)


@router.post("/reset_password", response_model=MessageSchema)
async def reset_password(
    body: EmailSchema,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> MessageSchema:
    user = await user_repo.get_user_by_email(body.email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND
        )
    background_tasks.add_task(
        email_service.send_reset_password_email,
        user,
        request.base_url,
    )
    return MessageSchema(message="Check your email for password reset instructions.")


@router.get("/reset_password/{reset_token}", response_model=MessageSchema)
async def reset_password_verified_email(
    reset_token: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> MessageSchema:
    email = await token_manager.get_email_from_token(reset_token)
    user = await user_repo.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=messages.VERIFICATION_ERROR,
        )

    new_password = password_manager.get_new_password(password_length=12)
    new_password_hash = password_manager.get_password_hash(new_password)
    await user_repo.update_password(user.id, new_password_hash, db)

    background_tasks.add_task(email_service.send_new_password_email, user, new_password)
    return MessageSchema(message="New password was sent to your email.")
