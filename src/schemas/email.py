from pydantic import EmailStr, BaseModel


class EmailSchema(BaseModel):
    email: EmailStr


class MessageSchema(BaseModel):
    message: str
