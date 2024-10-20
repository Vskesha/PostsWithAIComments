import pickle
from typing import Any

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.repository.abstract_repos import UserRepository
from src.schemas.users import UserRequest


class DBUserRepository(UserRepository):

    async def get_user_by_email(self, email: str, db: AsyncSession) -> User:
        stmt = select(User).filter_by(email=email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        return user

    async def create_user(self, body: UserRequest, db: AsyncSession) -> User:
        user = User(**body.model_dump(exclude_unset=True))
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def update_refresh_token(self, email: str, refresh_token: str, db: Any) -> User:
        user = await self.get_user_by_email(email, db)
        if user:
            user.refresh_token = refresh_token
            await db.commit()
            await db.refresh(user)
        return user


class RedisUserRepository(UserRepository):

    async def get_user_by_email(self, email: str, db: Redis) -> User:
        user = await db.get(f"users:{email}")
        if user:
            pickle.loads(user)
        return user

    async def create_user(self, body: dict, db: Redis) -> User:
        key = "users:" + body.get("email")
        user = body.get("user")
        await db.set(key, pickle.dumps(user))
        await  db.expire(key, 900)
        return user

    async def update_refresh_token(self, email: str, refresh_token: str, db: Any) -> User:
        pass

db_user_repo = DBUserRepository()
redis_user_repo = RedisUserRepository()
