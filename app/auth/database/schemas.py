from typing import Annotated, Optional
from datetime import datetime
import uuid

from pydantic import BaseModel, EmailStr, Field


class BaseUserModel(BaseModel):
    username: Annotated[str, Field(max_length=100)]
    email: Annotated[EmailStr, Field(max_length=100)]
    registered_at: datetime
    is_public: bool
    is_active: Optional[Annotated[bool, Field(default=True)]]
    is_superuser: Optional[Annotated[bool, Field(default=False)]]

    class Config:
        from_attributes = True


class UserCreate(BaseUserModel):
    password: Annotated[str, Field(min_length=8, max_length=150)]
    registered_at: Optional[Annotated[datetime, Field(default=datetime.now())]]


class UserUpdate(BaseModel):
    username: Optional[Annotated[str, Field(max_length=100)]] = None
    email: Optional[Annotated[EmailStr, Field(max_length=100)]] = None
    is_public: Optional[bool] = None


class Token(BaseModel):
    access_token: str
    refresh_token: uuid.UUID
    token_type: str
