from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.users import UserBaseId


class PostBase(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    content: str = Field(min_length=3)


class PostRequest(PostBase):
    user_id: int = Field(ge=1)


class PostResponse(PostBase):
    id: int = Field(ge=1)
    created_at: datetime
    updated_at: datetime
    user: UserBaseId

    class Config:
        from_attributes = True
