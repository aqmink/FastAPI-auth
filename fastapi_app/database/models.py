from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    user_id: int = Field(nullable=False, primary_key=True, index=True)
    username: str = Field(unique=True)
    email: str = Field(unique=True, index=True)
    password: str = Field()
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
