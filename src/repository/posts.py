from datetime import timedelta
from typing import List

from dateutil.parser import parse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Post
from src.repository.abstract_repos import PostRepository
from src.schemas.posts import PostRequest, PostBase, BlockSchema


class DBPostRepository(PostRepository):

    async def get_posts(
        self,
        db: AsyncSession,
        blocked: bool = False,
        limit: int = 20,
        offset: int = 0,
        user_id: int | None = None,
        date_from: str = None,
        date_to: str = None,
    ) -> List[Post]:
        stmt = select(Post).where(Post.blocked == blocked)
        if user_id:
            stmt = stmt.filter_by(user_id=user_id)
        if date_from:
            date_from = parse(date_from)
            stmt = stmt.filter(Post.created_at >= date_from)
        if date_to:
            date_to = parse(date_to)
            date_to += timedelta(days=1)
            stmt = stmt.filter(Post.created_at <= date_to)
        stmt = stmt.offset(offset).limit(limit)
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

    async def update_post(self, body: PostBase, post_id: int, db: AsyncSession) -> Post:
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

    async def block_post(self, body: BlockSchema, db: AsyncSession) -> Post:
        post = await self.get_post(body.id, db)
        if post:
            post.blocked = body.blocked
            await db.commit()
            await db.refresh(post)
        return post


post_repo: PostRepository = DBPostRepository()
