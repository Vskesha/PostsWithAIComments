from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import messages
from src.database.db import get_db
from src.database.models import Post, Role, User
from src.repository.posts import post_repo
from src.schemas.email import MessageSchema
from src.schemas.posts import BlockSchema, PostBase, PostRequest, PostResponse
from src.services.auth import auth_service
from src.services.moderate import moderate_service
from src.services.roles_access import admin_moderator_access

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=List[PostResponse])
async def get_posts(
    limit: int = Query(20, ge=10, le=500),
    offset: int = Query(0, ge=0),
    user_id: int = Query(default=None, ge=1),
    date_from: str = Query(None),
    date_to: str = Query(None),
    db: AsyncSession = Depends(get_db),
) -> List[Post]:
    print(f"{date_from=}, {date_to=}")
    posts = await post_repo.get_posts(
        db, False, limit, offset, user_id, date_from, date_to
    )
    return posts


@router.get(
    "/blocked",
    response_model=List[PostResponse],
    dependencies=[Depends(admin_moderator_access)],
)
async def get_blocked_posts(
    limit: int = Query(20, ge=10, le=500),
    offset: int = Query(0, ge=0),
    user_id: int | None = Query(default=None, ge=1),
    date_from: str = Query(None),
    date_to: str = Query(None),
    db: AsyncSession = Depends(get_db),
) -> List[Post]:
    posts = await post_repo.get_posts(
        db, True, limit, offset, user_id, date_from, date_to
    )
    return posts


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
) -> Post:
    post = await post_repo.get_post(post_id, db)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND
        )
    return post


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    body: PostBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Post:
    body = PostRequest(**body.model_dump(), user_id=current_user.id)
    post = await post_repo.create_post(body, db)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating post",
        )
    inapropriate = await moderate_service.includes_profanity(
        body.title + "\n" + body.content
    )
    if inapropriate:
        await post_repo.block_post(BlockSchema(id=post.id, blocked=True), db)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.INAPPROPRIATE
        )
    return post


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    body: PostBase,
    post_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Post:
    post = await post_repo.get_post(post_id, db)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND
        )

    if current_user.role == Role.user and post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.NOT_YOUR_POST
        )
    post = await post_repo.update_post(body, post_id, db)

    inapropriate = await moderate_service.includes_profanity(
        body.title + "\n" + body.content
    )
    if inapropriate:
        await post_repo.block_post(BlockSchema(id=post.id, blocked=True), db)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.INAPPROPRIATE
        )

    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    post = await post_repo.get_post(post_id, db)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND
        )
    if current_user.role == Role.user and post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.NOT_YOUR_POST
        )
    post = await post_repo.delete_post(post_id, db)
    return post


@router.patch(
    "/blocked/",
    response_model=MessageSchema,
    dependencies=[Depends(admin_moderator_access)],
)
async def block_post(
    body: BlockSchema,
    db: AsyncSession = Depends(get_db),
) -> MessageSchema:
    """
    Blocks a post. For admins and moderators only.

    :param body: BlockSchema: id and boolean for block
    :param db: AsyncSession: Database session
    :return: MessageSchema: A response indicating the successful block
    """
    post = await post_repo.get_post(body.id, db)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND
        )
    await post_repo.block_post(body, db)
    return MessageSchema(message=messages.BLOCKED)
