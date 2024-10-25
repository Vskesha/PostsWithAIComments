from abc import ABC, abstractmethod
from typing import List, Any

from src.database.models import Post, User, Token
from src.schemas.posts import PostBase, PostRequest
from src.schemas.tokens import TokenData
from src.schemas.users import UserRequest, ChangeRoleModel


class PostRepository(ABC):

    @abstractmethod
    async def get_posts(self, limit: int, offset: int, db: Any) -> List[Post]:
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
