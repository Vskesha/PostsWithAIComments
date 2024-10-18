import contextlib

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from src.conf.config import settings


class DatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        This method is a context manager that returns the database session.
        It also handles any exceptions that may occur during the session, and closes
        the connection when it's done.

        :return: A database session
        """
        if self._session_maker is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Session is not initialized",
            )
        session = self._session_maker()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
            )
        finally:
            await session.close()


SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
sessionmanager = DatabaseSessionManager(SQLALCHEMY_DATABASE_URL)


async def get_db():
    """
    The get_db function is a context manager that returns the database session.
    :return: A database session
    """
    async with sessionmanager.session() as session:
        yield session
