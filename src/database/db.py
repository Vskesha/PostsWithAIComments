from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError
from src.conf.config import settings

SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """
    The get_db function is a context manager that returns the database session.
    It also handles any exceptions that may occur during the session, and closes
    the connection when it's done.

    :return: A database session
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
    finally:
        db.close()
