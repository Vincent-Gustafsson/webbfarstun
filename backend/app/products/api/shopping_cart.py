from app.auth.deps import get_current_user
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from ...db import get_session
from ..models import ShoppingCart, User
from ..schemas import ShoppingCartCreate, ShoppingCartPublic, ShoppingCartUpdate

router = APIRouter(prefix="/cart", tags=["cart"])


def get_or_create_cart(session: Session, user_id: int) -> ShoppingCart:
    stmt = (
        select(ShoppingCart)
        .where(ShoppingCart.user_id == user_id)
        .options(
            selectinload(ShoppingCart.items).selectinload(ShoppingCartItem.product)
        )
    )
    cart = session.exec(stmt).first()
    if cart:
        return cart

    cart = ShoppingCart(user_id=user_id)
    session.add(cart)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        cart = session.exec(stmt).first()
        if cart is None:
            raise
        return cart

    session.refresh(cart)
    return cart


@router.get("/", response_model=ShoppingCartPublic, status_code=status.HTTP_200_OK)
def get_cart(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return get_or_create_cart(session, current_user.id)


"""
@router.post(
    "/", response_model=ShoppingCartPublic, status_code=status.HTTP_201_CREATED
)
def create_shopping_cart(
    *, session: Session = Depends(get_session), shopping_cart_data: ShoppingCartCreate
):
    if not session.get(User, shopping_cart_data.user_id):
        raise HTTPException(
            status_code=400, detail={"errors": {"user_id": "User not found"}}
        )

    user_cart_exists = session.exec(
        select(ShoppingCart).where(ShoppingCart.user_id == shopping_cart_data.user_id)
    ).first()
    if user_cart_exists:
        raise HTTPException(
            status_code=409,
            detail={
                "errors": {"user_id": "Shopping cart already exists for this user"}
            },
        )

    db_shopping_cart = ShoppingCart.model_validate(shopping_cart_data)
    session.add(db_shopping_cart)
    session.commit()
    session.refresh(db_shopping_cart)
    return db_shopping_cart


@router.get("/", response_model=list[ShoppingCartPublic])
def get_shopping_carts(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    shopping_carts = session.exec(
        select(ShoppingCart).offset(offset).limit(limit)
    ).all()
    return shopping_carts


@router.get("/{shopping_cart_id}", response_model=ShoppingCartPublic)
def get_shopping_cart(
    *, shopping_cart_id: int, session: Session = Depends(get_session)
):
    shopping_cart = session.get(ShoppingCart, shopping_cart_id)
    if not shopping_cart:
        raise HTTPException(
            status_code=404,
            detail={"errors": {"shopping_cart_id": "Shopping cart not found"}},
        )
    return shopping_cart


@router.patch("/{shopping_cart_id}", response_model=ShoppingCartPublic)
def update_shopping_cart(
    *,
    shopping_cart_id: int,
    shopping_cart_data: ShoppingCartUpdate,
    session: Session = Depends(get_session),
):
    db_shopping_cart = session.get(ShoppingCart, shopping_cart_id)
    if not db_shopping_cart:
        raise HTTPException(
            status_code=404,
            detail={"errors": {"shopping_cart_id": "Shopping cart not found"}},
        )

    update_dict = shopping_cart_data.model_dump(exclude_unset=True)

    if "user_id" in update_dict:
        if not session.get(User, update_dict["user_id"]):
            raise HTTPException(
                status_code=400, detail={"errors": {"user_id": "User not found"}}
            )

        user_cart_exists = session.exec(
            select(ShoppingCart).where(
                ShoppingCart.user_id == update_dict["user_id"],
                ShoppingCart.id != shopping_cart_id,
            )
        ).first()
        if user_cart_exists:
            raise HTTPException(
                status_code=409,
                detail={
                    "errors": {"user_id": "Shopping cart already exists for this user"}
                },
            )

    db_shopping_cart.sqlmodel_update(update_dict)
    session.add(db_shopping_cart)
    session.commit()
    session.refresh(db_shopping_cart)
    return db_shopping_cart


@router.delete("/{shopping_cart_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shopping_cart(
    *, shopping_cart_id: int, session: Session = Depends(get_session)
):
    shopping_cart = session.get(ShoppingCart, shopping_cart_id)
    if not shopping_cart:
        raise HTTPException(
            status_code=404,
            detail={"errors": {"shopping_cart_id": "Shopping cart not found"}},
        )
    session.delete(shopping_cart)
    session.commit()
    return None
"""
