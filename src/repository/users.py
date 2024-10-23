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

    async def update_refresh_token(self, email: str, refresh_token: str | None, db: Any) -> User:
        user = await self.get_user_by_email(email, db)
        if user:
            user.refresh_token = refresh_token
            await db.commit()
            await db.refresh(user)
        return user


db_user_repo = DBUserRepository()
