from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.repository.abstract_repos import UserRepository
from src.schemas.users import UserRequest


class DBUserRepository(UserRepository):

    async def confirm_email(self, email: str, db: AsyncSession) -> None:
        """
        Confirms the email of a user by setting the email_confirmed field to True.

        :param email: str: user's email address
        :param db: AsyncSession: connection to the database
        :return: None
        """
        user = await self.get_user_by_email(email, db)
        if user:
            user.email_confirmed = True
            await db.commit()

    async def create_user(self, body: UserRequest, db: AsyncSession) -> User:
        """
        Creates a new user in the database.

        :param body: UserRequest: user's data
        :param db: AsyncSession: connection to the database
        :return: User: the created user
        """

        user = User(**body.model_dump(exclude_unset=True))
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def get_user_by_email(self, email: str, db: AsyncSession) -> User:
        """
        Retrieves a user from the database by their email address.

        :param email: str: user's email address
        :param db: AsyncSession: connection to the database
        :return: User: the user with the given email address, or None if not found
        """

        stmt = select(User).filter_by(email=email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        return user

    async def get_user_by_id(self, user_id: int, db: AsyncSession) -> User:
        """
        Retrieves a user from the database by their ID.

        :param user_id: int: user's ID
        :param db: AsyncSession: connection to the database
        :return: User: the user with the given ID, or None if not found
        """
        stmt = select(User).filter_by(id=user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        return user

    async def update_password(self, user_id: int, password: str, db: Any) -> User:
        user = await self.get_user_by_id(user_id, db)
        if user:
            user.password = password
            await db.commit()
            await db.refresh(user)
        return user


user_repo: UserRepository = DBUserRepository()
