from fastapi import Depends

from auth.database.models import User, TokenSession
from database.base import ORMBase
from database.connection import get_session, AsyncSession


class UserObjects(ORMBase):
    model = User


class TokenSessionObjects(ORMBase):
    model = TokenSession


def get_user_objects_dependency(session: AsyncSession = Depends(get_session)):
    return UserObjects(session)


def get_token_objects_dependency(session: AsyncSession = Depends(get_session)):
    return TokenSessionObjects(session)
