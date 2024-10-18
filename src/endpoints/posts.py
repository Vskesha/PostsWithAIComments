from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.messages import POST_NOT_FOUND
from src.database.db import get_db
from src.repository.posts import db_post_repo
from src.schemas.posts import PostResponse, PostRequest

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=List[PostResponse])
async def get_posts(
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> List[PostResponse]:
    todos = await db_post_repo.get_posts(limit, offset, db)
    return todos


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
) -> PostResponse:
    post = await db_post_repo.get_post(post_id, db)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=POST_NOT_FOUND
        )
    return post


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    body: PostRequest,
    db: AsyncSession = Depends(get_db),
):
    post = await db_post_repo.create_post(body, db)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating post",
        )
    return post


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    body: PostRequest,
    post_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
) -> PostResponse:
    post = await db_post_repo.update_post(body, post_id, db)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=POST_NOT_FOUND
        )
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
):
    post = await db_post_repo.delete_post(post_id, db)
    return post
