import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Response, status, HTTPException, Depends
from bcrypt import checkpw, hashpw, gensalt

from auth.cookies import CookieTransport
from auth.jwt_strategy import JWTStrategy
from auth.database.queries import (
    UserObjects,
    TokenSessionObjects,
    get_token_objects_dependency, 
    get_user_objects_dependency,
)
from auth.database.models import User, TokenSession
from auth.database.schemas import Token
from config import REFRESH_TOKEN_EXPIRE_DAYS


class AuthServise:
    def __init__(
        self,
        refresh_sessions: TokenSessionObjects,
        users: UserObjects,
        cookies = CookieTransport(),
        strategy = JWTStrategy(),
    ):
        self.cookies = cookies
        self.strategy = strategy
        self.users = users
        self.refresh_sessions = refresh_sessions

    async def authenticate(
        self, 
        username: str, 
        password: str, 
    ) -> Token:
        user = await self.users.get(username=username)
        exception = HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        if not user:
            raise exception
        if not checkpw(password.encode(), user.password.encode()):
            raise exception
        token = await self.create_token(user)
        response = Response(status_code=status.HTTP_202_ACCEPTED)
        self.cookies.set_login_cookie(response, token.access_token, "access_token")
        self.cookies.set_login_cookie(response, token.refresh_token, "refresh_token")
        return token

    async def authorize(self, **user_data) -> Response:
        user = await self.users.get(username=user_data["username"])
        exception = HTTPException(status_code=status.HTTP_409_CONFLICT)
        if user:
            raise exception
        user = await self.users.get(email=user_data["email"])
        if user:
            raise exception
        user_data["password"] = hashpw(user_data["password"].encode(), gensalt())
        await self.users.create(**user_data)
        return Response(status_code=status.HTTP_201_CREATED)

    async def logout(self, response: Response, token: uuid.UUID) -> Response:
        await self.refresh_sessions.delete(
            TokenSession.refresh_token == token,
        )
        self.cookies.set_logout_cookie(response, "access_token")
        self.cookies.set_logout_cookie(response, "refresh_token")
        return response

    async def create_token(self, user: User) -> Token:
        access_token = await self.strategy.write_token(user)
        refresh_token = uuid.uuid4()
        await self.refresh_sessions.create(
            user_id=user.id,
            created_at=datetime.now(),
            refresh_token=refresh_token,
            expires=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )
        return Token(
            access_token=access_token, 
            refresh_token=refresh_token, 
            token_type="bearer"
        )

    async def refresh(self, response: Response, token: uuid.UUID) -> Token:
        refresh_session = await self.refresh_sessions.get(
            TokenSession.refresh_token == token
        )
        if not refresh_session:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        if refresh_session.created_at + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS) <= datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        user = await self.users.get(User.id == refresh_session.user_id)
        access_token = self.strategy.write_token(user.username)
        self.cookies.set_login_cookie(response, access_token, "access_token")
        self.cookies.set_login_cookie(response, refresh_token, "refresh_token")
        refresh_token = uuid.uuid4()
        await self.refresh_sessions.update(
            TokenSession.id == refresh_session.id,
            refresh_token=refresh_token,
            expires_in=REFRESH_TOKEN_EXPIRE_DAYS
        )
        return Token(
            access_token=access_token, 
            refresh_token=refresh_token, 
            token_type="baerer"
        )

    async def get_current_user(self, token: str) -> User:
        return await self.strategy.read_token(token, self.users)

    async def get_current_active_user(
        self,
        current_user: User = Depends(get_current_user),
    ) -> User:
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unactive user",
            )
        return current_user


def auth_servise_dependency(
    users: UserObjects = Depends(get_user_objects_dependency),
    refresh_sessions: TokenSessionObjects = Depends(get_token_objects_dependency),
):
    return AuthServise(
        users=users, 
        refresh_sessions=refresh_sessions
    )
