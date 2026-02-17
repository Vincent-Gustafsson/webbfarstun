from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from ..db import get_session
from ..products.models import User
from .config import COOKIE_NAME
from .tokens import decode_access_token

# IMPORTANT: tokenUrl should be relative so it works with root_path="/api"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


def get_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    # Prefer Authorization header; fall back to cookie
    if not token:
        token = request.cookies.get(COOKIE_NAME)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or missing user"
        )

    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not (user.is_admin or user.is_employee):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )
    return user
