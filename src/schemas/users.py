from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr


class UserRequest(UserBase):
    password: str = Field(min_length=6, max_length=16)


class UserBaseId(UserBase):
    id: int = Field(ge=1)


class UserResponse(UserBaseId):
    email_confirmed: bool
    role: str = Field()
    banned: bool

    class Config:
        from_attributes = True


class ChangePasswordSchema(BaseModel):
    old_password: str = Field(min_length=6, max_length=16)
    new_password: str = Field(min_length=6, max_length=16)
