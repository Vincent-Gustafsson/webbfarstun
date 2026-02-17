from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, select

from ...auth.deps import get_current_user
from ...auth.passwords import hash_password, verify_password
from ...auth.tokens import create_access_token
from ...db import get_session
from ..models import User
from ..schemas import TokenOut, UserCreate, UserPublic, UserRegister, UserUpdate

router = APIRouter(tags=["users"])


@router.post(
    "/auth/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
def register(payload: UserRegister, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

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
        raise HTTPException(status_code=400, detail="Email already registered")

    session.refresh(user)
    return user


@router.post("/auth/login", response_model=TokenOut)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    # OAuth2PasswordRequestForm uses "username" field; we treat it as email
    user = session.exec(select(User).where(User.email == form.username)).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad credentials"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user"
        )

    token = create_access_token(user_id=user.id)
    return TokenOut(access_token=token)


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
