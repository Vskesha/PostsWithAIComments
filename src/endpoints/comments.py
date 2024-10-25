from typing import List

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Path,
    Query,
    BackgroundTasks,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import messages
from src.database.db import get_db
from src.database.models import User, Role, Comment
from src.repository.comments import comment_repo
from src.schemas.comments import (
    CommentResponse,
    CommentBase,
    CommentRequest,
    CommentCreate,
)
from src.schemas.email import MessageSchema
from src.schemas.posts import BlockSchema
from src.services.auth import auth_service
from src.services.moderate import moderate_service
from src.services.roles_access import admin_moderator_access
from src.services.tasks import task_create_answer

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/", response_model=List[CommentResponse])
async def get_comments(
    user_id: int = Query(None, ge=1),
    post_id: int = Query(None, ge=1),
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> List[Comment]:
    comments = await comment_repo.get_comments(
        user_id, post_id, False, limit, offset, db
    )
    return comments


@router.get(
    "/blocked",
    response_model=List[CommentResponse],
    dependencies=[Depends(admin_moderator_access)],
)
async def get_blocked_comments(
    user_id: int = Query(None, ge=1),
    post_id: int = Query(None, ge=1),
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> List[Comment]:
    comments = await comment_repo.get_comments(
        user_id, post_id, True, limit, offset, db
    )
    return comments


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
) -> Comment:
    comment = await comment_repo.get_comment(comment_id, db)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND
        )
    return comment


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    body: CommentCreate,
    backgroundtasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Comment:
    body = CommentRequest(**body.model_dump(), user_id=current_user.id)
    comment = await comment_repo.create_comment(body, db)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating comment",
        )
    inapropriate = await moderate_service.includes_profanity(body.content)
    if inapropriate:
        await comment_repo.block_comment(BlockSchema(id=comment.id, blocked=True), db)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.INAPPROPRIATE
        )

    backgroundtasks.add_task(task_create_answer, comment, db)

    return comment


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    body: CommentBase,
    comment_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Comment:
    comment = await comment_repo.get_comment(comment_id, db)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND
        )

    if current_user.role == Role.user and comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.NOT_YOUR_COMMENT
        )
    comment = await comment_repo.update_comment(body, comment_id, db)

    inapropriate = await moderate_service.includes_profanity(body.content)
    if inapropriate:
        await comment_repo.block_comment(BlockSchema(id=comment.id, blocked=True), db)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.INAPPROPRIATE
        )

    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    comment = await comment_repo.get_comment(comment_id, db)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND
        )
    if current_user.role == Role.user and comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.NOT_YOUR_COMMENT
        )
    comment = await comment_repo.delete_comment(comment_id, db)
    return comment


@router.patch(
    "/blocked/",
    response_model=MessageSchema,
    dependencies=[Depends(admin_moderator_access)],
)
async def block_comment(
    body: BlockSchema,
    db: AsyncSession = Depends(get_db),
) -> MessageSchema:
    """
    Blocks a comment. For admins or moderators only.

    :param body: BlockSchema: id and boolean for blocking
    :param db: AsyncSession: Database session
    :return: MessageSchema: A response indicating the successful block
    """
    comment = await comment_repo.get_comment(comment_repo, db)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND
        )
    await comment_repo.block_comment(body, db)
    return MessageSchema(message=messages.BLOCKED)
