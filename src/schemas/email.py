from pydantic import BaseModel, EmailStr


class EmailSchema(BaseModel):
    email: EmailStr


class MessageSchema(BaseModel):
    message: str
