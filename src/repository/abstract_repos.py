from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any

from src.database.models import Post, User, Token, Comment, Answer
from src.schemas.answers import AnswerRequest, AnswerBase
from src.schemas.comments import CommentRequest, CommentBase
from src.schemas.posts import PostBase, PostRequest, BlockSchema
from src.schemas.tokens import TokenData
from src.schemas.users import UserRequest, ChangeRoleModel


class PostRepository(ABC):

    @abstractmethod
    async def get_posts(
        self,
        db: Any,
        blocked: bool = False,
        limit: int = 20,
        offset: int = 0,
        user_id: int | None = None,
        date_from: str = None,
        date_to: str = None,
    ) -> List[Post]:
        raise NotImplementedError

    @abstractmethod
    async def get_post(self, post_id, db: Any) -> Post:
        raise NotImplementedError

    @abstractmethod
    async def create_post(self, body: PostRequest, db: Any) -> Post:
        raise NotImplementedError

    @abstractmethod
    async def update_post(self, body: PostBase, post_id: int, db: Any) -> Post:
        raise NotImplementedError

    @abstractmethod
    async def delete_post(self, post_id: int, db: Any) -> Post:
        raise NotImplementedError

    @abstractmethod
    async def block_post(self, body: BlockSchema, db: Any) -> Post:
        raise NotImplementedError


class CommentRepository(ABC):

    @abstractmethod
    async def get_comments(
        self,
        db: Any,
        blocked: bool = False,
        limit: int = 20,
        offset: int = 0,
        user_id: int | None = None,
        post_id: int | None = None,
        date_from: str = None,
        date_to: str = None,
    ) -> List[Comment]:
        raise NotImplementedError

    @abstractmethod
    async def get_comment(self, comment_id, db: Any) -> Comment:
        raise NotImplementedError

    @abstractmethod
    async def create_comment(self, body: CommentRequest, db: Any) -> Comment:
        raise NotImplementedError

    @abstractmethod
    async def update_comment(
        self, body: CommentBase, comment_id: int, db: Any
    ) -> Comment:
        raise NotImplementedError

    @abstractmethod
    async def delete_comment(self, comment_id: int, db: Any) -> Comment:
        raise NotImplementedError

    @abstractmethod
    async def block_comment(self, body: BlockSchema, db: Any) -> Comment:
        raise NotImplementedError


class AnswerRepository(ABC):

    @abstractmethod
    async def get_answers(
        self,
        db: Any,
        blocked: bool = False,
        limit: int = 20,
        offset: int = 0,
        user_id: int | None = None,
        comment_id: int | None = None,
        date_from: str = None,
        date_to: str = None,
    ) -> List[Answer]:
        raise NotImplementedError

    @abstractmethod
    async def get_answer(self, answer_id, db: Any) -> Answer:
        raise NotImplementedError

    @abstractmethod
    async def create_answer(self, body: AnswerRequest, db: Any) -> Answer:
        raise NotImplementedError

    @abstractmethod
    async def update_answer(self, body: AnswerBase, answer_id: int, db: Any) -> Answer:
        raise NotImplementedError

    @abstractmethod
    async def delete_answer(self, answer_id: int, db: Any) -> Answer:
        raise NotImplementedError

    @abstractmethod
    async def block_answer(self, body: BlockSchema, db: Any) -> Answer:
        raise NotImplementedError


class TokenRepository(ABC):
    @abstractmethod
    async def add_token(self, body: TokenData, db: Any) -> Token:
        raise NotImplementedError

    @abstractmethod
    async def get_token(self, token_str: str, db: Any) -> Token:
        raise NotImplementedError

    @abstractmethod
    async def block_token(self, token_str: str, db: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    async def block_user_tokens(self, user_id: int, db: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    async def token_is_blocked(self, token_str: str, db: Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def delete_expired(self, db: Any) -> None:
        raise NotImplementedError


class UserRepository(ABC):

    @abstractmethod
    async def confirm_email(self, email: str, db: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    async def create_user(self, body: UserRequest, db: Any) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_email(self, email: str, db: Any) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_id(self, user_id: int, db: Any) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_users(self, limit: int, offset: int, db: Any) -> List[User]:
        raise NotImplementedError

    @abstractmethod
    async def update_password(self, user_id: int, password: str, db: Any) -> User:
        raise NotImplementedError

    @abstractmethod
    async def ban_user(self, user_id: int, db: Any) -> User:
        raise NotImplementedError

    @abstractmethod
    async def unban_user(self, user_id: int, db: Any) -> User:
        raise NotImplementedError

    @abstractmethod
    async def change_role(self, body: ChangeRoleModel, db: Any) -> User:
        raise NotImplementedError

    @abstractmethod
    async def set_answer_delay(self, user_id: int, delay: int | None, db: Any) -> User:
        raise NotImplementedError
