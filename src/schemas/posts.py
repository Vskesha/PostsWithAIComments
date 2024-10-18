from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.users import UserResponse


class PostRequest(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    content: str = Field(min_length=3)
    user_id: int = Field(ge=1)


class PostResponse(PostRequest):
    id: int = Field(ge=1)
    created_at: datetime
    updated_at: datetime
    # user: UserResponse

    class Config:
        orm_mode = True
