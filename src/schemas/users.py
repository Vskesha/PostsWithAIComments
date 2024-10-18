from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr

class UserRequest(UserBase):
    password: str = Field(min_length=3, max_length=255)


class UserResponse(UserBase):
    id: int = Field(ge=1)
    email_confirmed: bool
    role: str = Field()
    created_at: datetime
    updated_at: datetime
    status_active: bool

    class Config:
        from_attributes = True

        # id: Mapped[int] = mapped_column(primary_key=True)
        # username: Mapped[str] = mapped_column(String(50), nullable=False)
        # email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
        # email_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
        # password: Mapped[str] = mapped_column(String(255), nullable=False)
    # refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
        # created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
        # updated_at: Mapped[datetime] = mapped_column(
        #     DateTime, default=func.now(), onupdate=func.now()
        # )
        # role: Mapped[Role] = mapped_column(Enum(Role), default=Role.user, nullable=False)
    # status_active: Mapped[bool] = mapped_column(Boolean, default=True)
