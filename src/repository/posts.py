from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Post
from src.repository.abstract_repos import PostRepository
from src.schemas.posts import PostRequest, PostBase


class DBPostRepository(PostRepository):

    async def get_posts(self, limit: int, offset: int, db: AsyncSession) -> List[Post]:
        stmt = select(Post).offset(offset).limit(limit)
        result = await db.execute(stmt)
        posts = result.scalars().all()
        return list(posts)

    async def get_post(self, post_id, db: AsyncSession) -> Post:
        stmt = select(Post).filter_by(id=post_id)
        post = await db.execute(stmt)
        return post.scalar_one_or_none()

    async def create_post(self, body: PostRequest, db: AsyncSession) -> Post:
        post = Post(**body.model_dump(exclude_unset=True))
        db.add(post)
        await db.commit()
        await db.refresh(post)
        return post

    async def update_post(
        self, body: PostBase, post_id: int, db: AsyncSession
    ) -> Post:
        stmt = select(Post).filter_by(id=post_id)
        result = await db.execute(stmt)
        post = result.scalar_one_or_none()
        if post:
            post.title = body.title
            post.content = body.content
            await db.commit()
            await db.refresh(post)
        return post

    async def delete_post(self, post_id: int, db: AsyncSession) -> Post:
        stmt = select(Post).filter_by(id=post_id)
        result = await db.execute(stmt)
        post = result.scalar_one_or_none()
        if post:
            await db.delete(post)
            await db.commit()
        return post


db_post_repo = DBPostRepository()
