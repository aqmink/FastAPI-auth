from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Path, Response, Request
from fastapi.security import OAuth2PasswordRequestForm

from auth.backend import auth_servise_dependency, AuthServise
from auth.database.queries import get_user_objects_dependency, UserObjects
from auth.database.models import User
from auth.utils import OAuth2PasswordBearerWithCookie

router = APIRouter(prefix="/api/auth")

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="api/auth/sign-in")


@router.get("/users")
async def user_list(users: Annotated[UserObjects, Depends(get_user_objects_dependency)]):
    return await users.get_all()


@router.get("/users/{username}")
async def get_user(
    username: Annotated[str, Path()],
    users: Annotated[UserObjects, Depends(get_user_objects_dependency)],
):
    return await users.get(username=username)


@router.post("/sign-up")
async def sign_up(
    form_data: Annotated[User, Depends()],
    servise: Annotated[AuthServise, Depends(auth_servise_dependency)],
):
    return await servise.authorize(**form_data.model_dump())


@router.post("/sign-in")
async def sign_in(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    servise: Annotated[AuthServise, Depends(auth_servise_dependency)],
):
    return await servise.authenticate(form_data.username, form_data.password)


@router.get("/my_profile")
async def get_current_user_profile(
    servise: Annotated[AuthServise, Depends(auth_servise_dependency)],
    token: Annotated[str, Depends(oauth2_scheme)],
):
    return await servise.get_current_active_user(token)


@router.post("/logout")
async def logout(
    servise: Annotated[AuthServise, Depends(auth_servise_dependency)],
    request: Request,
    response: Response,
):
    token = request.cookies.get("refres_token")
    return await servise.logout(response, token)


@router.post("/refresh")
async def refresh(
    servise: Annotated[AuthServise, Depends(auth_servise_dependency)],
    request: Request,
    response: Response,
):
    token = request.cookies.get("refresh_token")
    return await servise.refresh(response, token)
