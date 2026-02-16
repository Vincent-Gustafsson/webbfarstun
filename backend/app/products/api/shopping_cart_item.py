from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from ...db import get_session
from ..models import Product, ShoppingCart, ShoppingCartItem
from ..schemas import (
    ShoppingCartItemCreate,
    ShoppingCartItemPublic,
    ShoppingCartItemUpdate,
)

router = APIRouter(prefix="/shopping-cart-items", tags=["shopping-cart-items"])


@router.post(
    "/", response_model=ShoppingCartItemPublic, status_code=status.HTTP_201_CREATED
)
def create_shopping_cart_item(
    *,
    session: Session = Depends(get_session),
    shopping_cart_item_data: ShoppingCartItemCreate,
):
    if not session.get(Product, shopping_cart_item_data.product_id):
        raise HTTPException(
            status_code=400, detail={"errors": {"product_id": "Product not found"}}
        )

    if not session.get(ShoppingCart, shopping_cart_item_data.shopping_cart_id):
        raise HTTPException(
            status_code=400,
            detail={"errors": {"shopping_cart_id": "Shopping cart not found"}},
        )

    db_shopping_cart_item = ShoppingCartItem.model_validate(shopping_cart_item_data)
    session.add(db_shopping_cart_item)
    session.commit()
    session.refresh(db_shopping_cart_item)
    return db_shopping_cart_item


@router.get("/", response_model=list[ShoppingCartItemPublic])
def get_shopping_cart_items(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    shopping_cart_items = session.exec(
        select(ShoppingCartItem).offset(offset).limit(limit)
    ).all()
    return shopping_cart_items


@router.get("/{shopping_cart_item_id}", response_model=ShoppingCartItemPublic)
def get_shopping_cart_item(
    *, shopping_cart_item_id: int, session: Session = Depends(get_session)
):
    shopping_cart_item = session.get(ShoppingCartItem, shopping_cart_item_id)
    if not shopping_cart_item:
        raise HTTPException(
            status_code=404,
            detail={
                "errors": {"shopping_cart_item_id": "Shopping cart item not found"}
            },
        )
    return shopping_cart_item


@router.patch("/{shopping_cart_item_id}", response_model=ShoppingCartItemPublic)
def update_shopping_cart_item(
    *,
    shopping_cart_item_id: int,
    shopping_cart_item_data: ShoppingCartItemUpdate,
    session: Session = Depends(get_session),
):
    db_shopping_cart_item = session.get(ShoppingCartItem, shopping_cart_item_id)
    if not db_shopping_cart_item:
        raise HTTPException(
            status_code=404,
            detail={
                "errors": {"shopping_cart_item_id": "Shopping cart item not found"}
            },
        )

    update_dict = shopping_cart_item_data.model_dump(exclude_unset=True)

    if "product_id" in update_dict and not session.get(
        Product, update_dict["product_id"]
    ):
        raise HTTPException(
            status_code=400, detail={"errors": {"product_id": "Product not found"}}
        )

    if "shopping_cart_id" in update_dict and not session.get(
        ShoppingCart, update_dict["shopping_cart_id"]
    ):
        raise HTTPException(
            status_code=400,
            detail={"errors": {"shopping_cart_id": "Shopping cart not found"}},
        )

    db_shopping_cart_item.sqlmodel_update(update_dict)
    session.add(db_shopping_cart_item)
    session.commit()
    session.refresh(db_shopping_cart_item)
    return db_shopping_cart_item


@router.delete("/{shopping_cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shopping_cart_item(
    *, shopping_cart_item_id: int, session: Session = Depends(get_session)
):
    shopping_cart_item = session.get(ShoppingCartItem, shopping_cart_item_id)
    if not shopping_cart_item:
        raise HTTPException(
            status_code=404,
            detail={
                "errors": {"shopping_cart_item_id": "Shopping cart item not found"}
            },
        )
    session.delete(shopping_cart_item)
    session.commit()
    return None
