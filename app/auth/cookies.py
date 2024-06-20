from typing import Literal, Optional

from fastapi import Response
from fastapi.security import APIKeyCookie


class CookieTransport:
    scheme: APIKeyCookie

    def __init__(
        self,
        cookie_max_age: Optional[int] = None,
        cookie_path: str = "/",
        cookie_domain: Optional[str] = None,
        cookie_secure: bool = True,
        cookie_httponly: bool = True,
        cookie_samesite: Literal["lax", "strict", "none"] = "lax",
    ):
        self.cookie_max_age = cookie_max_age
        self.cookie_path = cookie_path
        self.cookie_domain = cookie_domain
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.cookie_samesite = cookie_samesite

    def set_login_cookie(
        self, 
        response: Response,
        content: str,
        key: str,
    ) -> Response:
        response.set_cookie(
            key=key,
            value=content,
            max_age=self.cookie_max_age,
            path=self.cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )
        return response

    def set_logout_cookie(self, response: Response, key: str) -> Response:
        response.delete_cookie(
            key=key,
            path=self.cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )
        return response
