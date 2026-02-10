from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from ...db import get_session
from ..models import User
from ..schemas import UserCreate, UserPublic, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def create_user(*, session: Session = Depends(get_session), user_data: UserCreate):
    existing = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    db_user = User.model_validate(user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/", response_model=list[UserPublic])
def get_users(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@router.get("/{user_id}", response_model=UserPublic)
def get_user(*, user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserPublic)
def update_user(
    *,
    user_id: int,
    user_data: UserUpdate,
    session: Session = Depends(get_session),
):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_dict = user_data.model_dump(exclude_unset=True)

    # Optional: enforce email uniqueness if you allow updating email
    # if "email" in update_dict:
    #     existing = session.exec(
    #         select(User).where(User.email == update_dict["email"], User.id != user_id)
    #     ).first()
    #     if existing:
    #         raise HTTPException(status_code=400, detail="Email already exists")

    db_user.sqlmodel_update(update_dict)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(*, user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return None
