"""
Session handling — no auth required for MVP.
A UUID is stored in a cookie on first visit, valid for 1 year.
"""

import os
import uuid
from fastapi import Request, Response

SESSION_COOKIE = "entropy_session"
COOKIE_MAX_AGE = 365 * 24 * 3600  # 1 year
DEFAULT_SHOWCASE_USER_ID = "00000000-0000-4000-8000-000000000120"


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_user_id(request: Request, response: Response) -> str:
    """Read/create a session id, or use the seeded showcase identity locally."""
    if _env_flag("SHOWCASE_MODE"):
        user_id = os.getenv("SHOWCASE_USER_ID", DEFAULT_SHOWCASE_USER_ID)
        response.set_cookie(
            SESSION_COOKIE,
            user_id,
            max_age=COOKIE_MAX_AGE,
            httponly=True,
            samesite="lax",
        )
        return user_id

    user_id = request.cookies.get(SESSION_COOKIE)
    if not user_id:
        user_id = str(uuid.uuid4())
        response.set_cookie(
            SESSION_COOKIE,
            user_id,
            max_age=COOKIE_MAX_AGE,
            httponly=True,
            samesite="lax",
        )
    return user_id
