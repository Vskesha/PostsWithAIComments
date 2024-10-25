import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Comment
from src.repository.answers import answer_repo
from src.schemas.answers import AnswerRequest
from src.services.ai import ai_service


async def task_create_answer(comment: Comment, db: AsyncSession):
    post = comment.post
    post_creator = post.user
    delay = post_creator.answer_delay
    if delay is not None:
        prompt = (
            f"Imagine You are the author of the post: \n{post.title}\n{post.content}\n"
            f"You received the comment: \n{comment.content}\n"
            f"Write a short answer to this comment"
        )
        answer_text = await ai_service.get_response(prompt)
        body = AnswerRequest(
            content=answer_text,
            comment_id=comment.id,
            user_id=post_creator.id,
        )
        await asyncio.sleep(delay)
        await answer_repo.create_answer(body, db)
