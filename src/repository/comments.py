from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Comment
from src.repository.abstract_repos import CommentRepository
from src.schemas.comments import CommentBase, CommentRequest
from src.schemas.posts import BlockSchema


class DBCommentRepository(CommentRepository):

    async def get_comments(
        self,
        user_id: int | None,
        post_id: int | None,
        blocked: bool,
        limit: int,
        offset: int,
        db: AsyncSession,
    ) -> List[Comment]:
        stmt = select(Comment).where(Comment.blocked == blocked)
        if user_id:
            stmt = stmt.filter_by(user_id=user_id)
        if post_id:
            stmt = stmt.filter_by(post_id=post_id)
        stmt = stmt.offset(offset).limit(limit)
        result = await db.execute(stmt)
        comments = result.scalars().all()
        return list(comments)

    async def get_comment(self, comment_id, db: AsyncSession) -> Comment:
        stmt = select(Comment).filter_by(id=comment_id)
        comment = await db.execute(stmt)
        return comment.scalar_one_or_none()

    async def create_comment(self, body: CommentRequest, db: AsyncSession) -> Comment:
        comment = Comment(**body.model_dump(exclude_unset=True))
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        return comment

    async def update_comment(
        self, body: CommentBase, comment_id: int, db: AsyncSession
    ) -> Comment:
        comment = await self.get_comment(comment_id, db)
        if comment:
            comment.content = body.content
            await db.commit()
            await db.refresh(comment)
        return comment

    async def delete_comment(self, comment_id: int, db: AsyncSession) -> Comment:
        comment = await self.get_comment(comment_id, db)
        if comment:
            await db.delete(comment)
            await db.commit()
        return comment

    async def block_comment(self, body: BlockSchema, db: AsyncSession) -> Comment:
        comment = await self.get_comment(body.id, db)
        if comment:
            comment.blocked = body.blocked
            await db.commit()
            await db.refresh(comment)
        return comment


comment_repo: CommentRepository = DBCommentRepository()
