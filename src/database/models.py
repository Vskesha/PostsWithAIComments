import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, func, Integer, String, Text
from sqlalchemy.orm import relationship

from src.database.db import Base, engine


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    __tablename__ = "users"
    id = Column(primary_key=True)
    username = Column(String(50))
    email = Column(String(150), nullable=False, unique=True)
    email_confirmed = Column(Boolean, default=False, nullable=True)
    password = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    role = Column(Enum(Role), default=Role.admin, nullable=True)
    status_active = Column(Boolean, default=True)


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="posts")


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    post = relationship("Post", backref="comments")


class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=False)
    comment = relationship("Comment", backref="answers")


Base.metadata.create_all(bind=engine)