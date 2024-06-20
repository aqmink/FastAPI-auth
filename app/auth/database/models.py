from uuid import UUID

from datetime import datetime, timedelta

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "Users"

    id: int = Field(nullable=False, primary_key=True, index=True)
    username: str = Field(unique=True, max_length=150)
    email: str = Field(unique=True, max_length=150)
    password: str = Field()
    registered_at: datetime = Field(default=datetime.now())
    is_public: bool = Field()
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)


class TokenSession(SQLModel, table=True):
    id: int = Field(nullable=False, primary_key=True, index=True)
    refresh_token: UUID = Field(unique=True, index=True)
    created_at: datetime = Field(default=datetime.now().date())
    expires: timedelta = Field()
    user_id: int | None = Field(default=None, foreign_key="Users.id")
