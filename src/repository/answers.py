from datetime import timedelta
from typing import List

from dateutil.parser import parse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Answer
from src.repository.abstract_repos import AnswerRepository
from src.schemas.answers import AnswerBase, AnswerRequest
from src.schemas.posts import BlockSchema


class DBAnswerRepository(AnswerRepository):

    async def get_answers(
        self,
        db: AsyncSession,
        blocked: bool = False,
        limit: int = 20,
        offset: int = 0,
        user_id: int | None = None,
        comment_id: int | None = None,
        date_from: str = None,
        date_to: str = None,
    ) -> List[Answer]:
        stmt = select(Answer).where(Answer.blocked == blocked)
        if user_id:
            stmt = stmt.filter_by(user_id=user_id)
        if comment_id:
            stmt = stmt.filter_by(comment_id=comment_id)
        if date_from:
            date_from = parse(date_from)
            stmt = stmt.filter(Answer.created_at >= date_from)
        if date_to:
            date_to = parse(date_to)
            date_to += timedelta(days=1)
            stmt = stmt.filter(Answer.created_at <= date_to)
        stmt = stmt.offset(offset).limit(limit)
        result = await db.execute(stmt)
        answers = result.scalars().all()
        return list(answers)

    async def get_answer(self, answer_id, db: AsyncSession) -> Answer:
        stmt = select(Answer).filter_by(id=answer_id)
        answer = await db.execute(stmt)
        return answer.scalar_one_or_none()

    async def create_answer(self, body: AnswerRequest, db: AsyncSession) -> Answer:
        answer = Answer(**body.model_dump(exclude_unset=True))
        db.add(answer)
        await db.commit()
        await db.refresh(answer)
        return answer

    async def update_answer(
        self, body: AnswerBase, answer_id: int, db: AsyncSession
    ) -> Answer:
        answer = await self.get_answer(answer_id, db)
        if answer:
            answer.content = body.content
            await db.commit()
            await db.refresh(answer)
        return answer

    async def delete_answer(self, answer_id: int, db: AsyncSession) -> Answer:
        answer = await self.get_answer(answer_id, db)
        if answer:
            await db.delete(answer)
            await db.commit()
        return answer

    async def block_answer(self, body: BlockSchema, db: AsyncSession) -> Answer:
        answer = await self.get_answer(body.id, db)
        if answer:
            answer.blocked = body.blocked
            await db.commit()
            await db.refresh(answer)
        return answer


answer_repo: AnswerRepository = DBAnswerRepository()
