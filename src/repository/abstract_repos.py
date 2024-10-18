from abc import ABC, abstractmethod
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Post, User
from src.schemas.posts import PostRequest
from src.schemas.users import UserRequest


class PostRepository(ABC):

    @abstractmethod
    async def get_posts(self, limit: int, offset: int, db: AsyncSession) -> List[Post]:
        raise NotImplementedError

    @abstractmethod
    async def get_post(self, post_id, db: AsyncSession) -> Post:
        raise NotImplementedError

    @abstractmethod
    async def create_post(self, body: PostRequest, db: AsyncSession) -> Post:
        raise NotImplementedError

    @abstractmethod
    async def update_post(
        self, body: PostRequest, post_id: int, db: AsyncSession
    ) -> Post:
        raise NotImplementedError

    @abstractmethod
    async def delete_post(self, post_id: int, db: AsyncSession) -> Post:
        raise NotImplementedError


class UserRepository(ABC):

    @abstractmethod
    async def get_user_by_email(self, email: str, db: AsyncSession) -> User:
        raise NotImplementedError

    @abstractmethod
    async def create_user(self, body: UserRequest, db: AsyncSession) -> User:
        raise NotImplementedError
