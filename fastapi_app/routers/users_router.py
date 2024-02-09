from typing import Annotated, Optional
from datetime import datetime, timedelta

from bcrypt import checkpw
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.security import (
    OAuth2PasswordBearer, 
    OAuth2PasswordRequestForm
)
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_session
from database.schemas import Token, TokenData, UserCreate, UserModel
from database.queries import create_user, get_users, get_user
from config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[],
    responses={404: {"Not found": "users"}},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

templates = Jinja2Templates(directory="website_app/templates")


async def create_access_token(
    data: dict, expires_delta: timedelta | None = None
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_session),
):
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token=token, key=SECRET_KEY, algorithms=[ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise exception
        token_data = TokenData(username=username)
    except JWTError:
        raise exception
    user = get_user(session=session, username=token_data.username)
    if not user:
        raise exception
    return user


async def get_current_active_user(
    current_user: Annotated[UserModel, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.get("/", response_class=HTMLResponse)
async def get_user_list(
    request: Request,
    user: Annotated[Optional[UserModel], Depends()], 
    session: AsyncSession = Depends(get_session)
):
    users = await get_users(
        session=session, 
        user_id=user.user_id, 
        username=user.username, 
        email=user.email,
    )
    return templates.TemplateResponse(
        request, "index.html", {"users": users}
    )


@router.post("/sign-up", response_class=HTMLResponse)
async def sign_up(
    request: Request,
    form: Annotated[UserCreate, Depends()], 
    session: AsyncSession = Depends(get_session)
):
    if form.password1 != form.password2:
        raise HTTPException(400, "Passwords are not the same")
    try:
        await create_user(user=form, session=session)
    except ValueError:
        raise HTTPException(400, "User with this username already exists")
    return form


@router.post("/sign-in")
async def sign_in(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session)
) -> Token:  
    user = await get_user(session=session, username=form.username)
    if not user:
        raise HTTPException(400, "Incorrect usernmame or password")
    if not checkpw(form.password.encode(), user.password.encode()):
        raise HTTPException(400, "Incorrect usernmame or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
