from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ...db import get_session
from ..models import Order, User
from ..schemas import OrderPublic

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/{user_id}", response_model=list[OrderPublic])
def get_orders_for_user(*, user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=404, detail={"errors": {"user": "User not found"}}
        )

    orders = session.exec(
        select(Order)
        .where(Order.user_id == user_id)
        .order_by(Order.purchased_at.desc(), Order.id.desc())
    ).all()
    return orders


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(*, order_id: int, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(
            status_code=404, detail={"errors": {"order": "Order not found"}}
        )

    session.delete(order)
    session.commit()
    return None
