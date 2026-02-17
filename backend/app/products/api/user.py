from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, select

from ...auth.config import (
    COOKIE_MAX_AGE,
    COOKIE_NAME,
    COOKIE_PATH,
    COOKIE_SAMESITE,
    COOKIE_SECURE,
)
from ...auth.deps import get_current_user
from ...auth.passwords import hash_password, verify_password
from ...auth.tokens import create_access_token
from ...db import get_session
from ..models import User
from ..schemas import TokenOut, UserPublic, UserRegister, UserUpdate

router = APIRouter(tags=["users"])


@router.post(
    "/auth/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
def register(payload: UserRegister, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(
            status_code=400, detail={"errors": {"Email": "Email already registered"}}
        )

    user = User(
        email=payload.email,
        name=payload.name,
        password_hash=hash_password(payload.password),
        is_admin=False,
        is_employee=False,
        is_active=True,
    )
    session.add(user)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=400, detail={"errors": {"Email": "Email already registered"}}
        )

    session.refresh(user)
    return user


@router.post("/auth/login", response_model=TokenOut)
def login(
    response: Response,
    form: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.email == form.username)).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"errors": {"Credentials": "Invalid credentials"}},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"errors": {"is_active": "Inactive user"}},
        )

    token = create_access_token(user_id=user.id)

    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,  # "lax"
        path=COOKIE_PATH,
        max_age=COOKIE_MAX_AGE,
    )

    return TokenOut(access_token=token)


@router.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie(
        key=COOKIE_NAME,
        path=COOKIE_PATH,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
    )
    return {"ok": True}


@router.get("/users/me", response_model=UserPublic)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/users/", response_model=list[UserPublic])
def get_users(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@router.get("/users/{user_id}", response_model=UserPublic)
def get_user(*, user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=404, detail={"errors": {"user": "User not found"}}
        )
    return user


@router.patch("/users/{user_id}", response_model=UserPublic)
def update_user(
    *,
    user_id: int,
    user_data: UserUpdate,
    session: Session = Depends(get_session),
):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404, detail={"errors": {"user": "User not found"}}
        )

    update_dict = user_data.model_dump(exclude_unset=True)

    db_user.sqlmodel_update(update_dict)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(*, user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=404, detail={"errors": {"user": "User not found"}}
        )
    session.delete(user)
    session.commit()
    return None
