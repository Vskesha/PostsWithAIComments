from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Answer
from src.repository.abstract_repos import AnswerRepository
from src.schemas.answers import AnswerBase, AnswerRequest
from src.schemas.posts import BlockSchema


class DBAnswerRepository(AnswerRepository):

    async def get_answers(
        self,
        user_id: int | None,
        comment_id: int | None,
        blocked: bool,
        limit: int,
        offset: int,
        db: AsyncSession,
    ) -> List[Answer]:
        stmt = select(Answer).where(Answer.blocked == blocked)
        if user_id:
            stmt = stmt.filter_by(user_id=user_id)
        if comment_id:
            stmt = stmt.filter_by(comment_id=comment_id)
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
