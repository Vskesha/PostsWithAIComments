from datetime import datetime

from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    content: str = Field(min_length=3)

class CommentCreate(CommentBase):
    post_id: int = Field(ge=1)

class CommentRequest(CommentCreate):
    user_id: int = Field(ge=1)


class CommentResponse(CommentRequest):
    id: int = Field(ge=1)
    blocked: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
