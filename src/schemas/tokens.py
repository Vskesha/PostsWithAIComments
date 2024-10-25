from datetime import datetime

from pydantic import BaseModel

from src.schemas.users import UserResponse


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    token: str
    expires: datetime
    blocked: bool = False
    user_id: int


class TokenResponse(TokenData):
    user: UserResponse