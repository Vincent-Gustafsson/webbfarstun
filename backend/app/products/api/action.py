from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from ...db import get_session
from ..models import Action, User
from ..schemas import ActionCreate, ActionPublic, ActionUpdate

router = APIRouter(prefix="/actions", tags=["actions"])


@router.post("/", response_model=ActionPublic, status_code=status.HTTP_201_CREATED)
def create_action(
    *, session: Session = Depends(get_session), action_data: ActionCreate
):
    if not session.get(User, action_data.user_id):
        raise HTTPException(
            status_code=400, detail={"errors": {"user_id": "User not found"}}
        )

    db_action = Action.model_validate(action_data)
    session.add(db_action)
    session.commit()
    session.refresh(db_action)
    return db_action


@router.get("/", response_model=list[ActionPublic])
def get_actions(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    actions = session.exec(select(Action).offset(offset).limit(limit)).all()
    return actions


@router.get("/{action_id}", response_model=ActionPublic)
def get_action(*, action_id: int, session: Session = Depends(get_session)):
    action = session.get(Action, action_id)
    if not action:
        raise HTTPException(
            status_code=404, detail={"errors": {"action_id": "Action not found"}}
        )
    return action


@router.patch("/{action_id}", response_model=ActionPublic)
def update_action(
    *,
    action_id: int,
    action_data: ActionUpdate,
    session: Session = Depends(get_session),
):
    db_action = session.get(Action, action_id)
    if not db_action:
        raise HTTPException(
            status_code=404, detail={"errors": {"action_id": "Action not found"}}
        )

    update_dict = action_data.model_dump(exclude_unset=True)

    if "user_id" in update_dict and not session.get(User, update_dict["user_id"]):
        raise HTTPException(
            status_code=400, detail={"errors": {"user_id": "User not found"}}
        )

    db_action.sqlmodel_update(update_dict)
    session.add(db_action)
    session.commit()
    session.refresh(db_action)
    return db_action


@router.delete("/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_action(*, action_id: int, session: Session = Depends(get_session)):
    action = session.get(Action, action_id)
    if not action:
        raise HTTPException(
            status_code=404, detail={"errors": {"action_id": "Action not found"}}
        )
    session.delete(action)
    session.commit()
    return None
