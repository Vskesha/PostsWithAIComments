from abc import ABC, abstractmethod
from typing import List, Any

from src.database.models import Post, User
from src.schemas.posts import PostBase, PostRequest
from src.schemas.users import UserRequest


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
    async def update_refresh_token(
        self, email: str, refresh_token: str | None, db: Any
    ) -> User:
        raise NotImplementedError
