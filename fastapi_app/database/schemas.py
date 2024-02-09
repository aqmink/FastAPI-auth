from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr
from fastapi import Form


class UserModel(BaseModel):
    user_id: Optional[int]
    username: Optional[str]
    email: Optional[EmailStr]


class UserCreate(BaseModel):
    username: Annotated[str, Form()]
    email: Annotated[EmailStr, Form()]
    password1: Annotated[str, Form()]
    password2: Annotated[str, Form()]
    
    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
