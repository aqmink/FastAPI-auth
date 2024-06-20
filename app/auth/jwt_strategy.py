from typing import Optional
from datetime import datetime, timedelta, UTC

from jose import jwt, JWTError
from fastapi import HTTPException, status

from config import ALGORITHM, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from .database.queries import UserObjects
from .database.models import User


class JWTStrategy:
    def __init__(
        self,
        secret: str = SECRET_KEY,
        algorithm: Optional[str] = ALGORITHM,
        life_time: Optional[int] = ACCESS_TOKEN_EXPIRE_MINUTES,
    ):
        self.secret = secret
        self.algorithm = algorithm
        self.life_time = life_time

    async def read_token(
        self, 
        token: Optional[str], 
        users: UserObjects
    ) -> User | None:
        try:
            data = jwt.decode(
                token=token, 
                key=self.secret, 
                algorithms=[self.algorithm],
            )
            username = data.get("sub")
        except JWTError as error:
            print(error)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return await users.get(username=username)

    async def write_token(self, user: User) -> str:
        to_encode = {
            "sub": user.username,
            "exp": datetime.now(tz=UTC) + timedelta(minutes=self.life_time),
        }
        encoded_jwt = jwt.encode(
            to_encode, 
            key=self.secret, 
            algorithm=self.algorithm,
        )
        return f"Bearer {encoded_jwt}"

    async def destroy_token(self):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
