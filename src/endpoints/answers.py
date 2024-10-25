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
from src.database.models import User, Role, Answer
from src.repository.answers import answer_repo
from src.schemas.answers import (
    AnswerResponse,
    AnswerBase,
    AnswerRequest,
    AnswerCreate,
)
from src.schemas.email import MessageSchema
from src.schemas.posts import BlockSchema
from src.services.auth import auth_service
from src.services.moderate import moderate_service
from src.services.roles_access import admin_moderator_access

router = APIRouter(prefix="/answers", tags=["answers"])


@router.get("/", response_model=List[AnswerResponse])
async def get_answers(
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    user_id: int = Query(None, ge=1),
    comment_id: int = Query(None, ge=1),
    date_from: str = Query(None),
    date_to: str = Query(None),
    db: AsyncSession = Depends(get_db),
) -> List[Answer]:
    answers = await answer_repo.get_answers(
        db, False, limit, offset, user_id, comment_id, date_from, date_to
    )
    return answers


@router.get(
    "/blocked",
    response_model=List[AnswerResponse],
    dependencies=[Depends(admin_moderator_access)],
)
async def get_blocked_answers(
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    user_id: int = Query(None, ge=1),
    comment_id: int = Query(None, ge=1),
    date_from: str = Query(None),
    date_to: str = Query(None),
    db: AsyncSession = Depends(get_db),
) -> List[Answer]:
    answers = await answer_repo.get_answers(
        db, True, limit, offset, user_id, comment_id, date_from, date_to
    )
    return answers


@router.get("/{answer_id}", response_model=AnswerResponse)
async def get_answer(
    answer_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
) -> Answer:
    answer = await answer_repo.get_answer(answer_id, db)
    if answer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.ANSWER_NOT_FOUND
        )
    return answer


@router.post("/", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
async def create_answer(
    body: AnswerCreate,
    backgroundtasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Answer:
    body = AnswerRequest(**body.model_dump(), user_id=current_user.id)
    answer = await answer_repo.create_answer(body, db)
    if answer is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating answer",
        )
    inapropriate = await moderate_service.includes_profanity(body.content)
    if inapropriate:
        await answer_repo.block_answer(BlockSchema(id=answer.id, blocked=True), db)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.INAPPROPRIATE
        )

    return answer


@router.put("/{answer_id}", response_model=AnswerResponse)
async def update_answer(
    body: AnswerBase,
    answer_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Answer:
    answer = await answer_repo.get_answer(answer_id, db)
    if answer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.ANSWER_NOT_FOUND
        )

    if current_user.role == Role.user and answer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.NOT_YOUR_ANSWER
        )
    answer = await answer_repo.update_answer(body, answer_id, db)

    inapropriate = await moderate_service.includes_profanity(body.content)
    if inapropriate:
        await answer_repo.block_answer(BlockSchema(id=answer.id, blocked=True), db)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.INAPPROPRIATE
        )

    return answer


@router.delete("/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_answer(
    answer_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    answer = await answer_repo.get_answer(answer_id, db)
    if answer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.ANSWER_NOT_FOUND
        )
    if current_user.role == Role.user and answer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.NOT_YOUR_ANSWER
        )
    answer = await answer_repo.delete_answer(answer_id, db)
    return answer


@router.patch(
    "/blocked/",
    response_model=MessageSchema,
    dependencies=[Depends(admin_moderator_access)],
)
async def block_answer(
    body: BlockSchema,
    db: AsyncSession = Depends(get_db),
) -> MessageSchema:
    """
    Blocks an answer. For admins or moderators only.

    :param body: BlockSchema: id and boolean for blocking
    :param db: AsyncSession: Database session
    :return: MessageSchema: A response indicating the successful block
    """
    answer = await answer_repo.get_answer(answer_repo, db)
    if answer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.ANSWER_NOT_FOUND
        )
    await answer_repo.block_answer(body, db)
    return MessageSchema(message=messages.BLOCKED)
