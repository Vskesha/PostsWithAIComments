from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BookModel(Base):
    __tablename__ = "books"
    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
