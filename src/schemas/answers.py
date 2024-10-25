from datetime import datetime

from pydantic import BaseModel, Field

class AnswerBase(BaseModel):
    content: str = Field(min_length=3)

class AnswerCreate(AnswerBase):
    comment_id: int = Field(ge=1)

class AnswerRequest(AnswerCreate):
    user_id: int = Field(ge=1)


class AnswerResponse(AnswerRequest):
    id: int = Field(ge=1)
    blocked: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
