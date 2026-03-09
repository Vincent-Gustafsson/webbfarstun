from app.auth.deps import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, delete, select

from ...db import get_session
from ..models import Order, Product, ProductImage, ShoppingCart, ShoppingCartItem, User
from ..schemas import (
    ShoppingCartItemCreateInCart,
    ShoppingCartItemPublic,
    ShoppingCartItemUpdate,
    ShoppingCartPublic,
)

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


def build_cart_public(session: Session, cart: ShoppingCart) -> ShoppingCartPublic:
    cart_items = []
    for item in cart.items:
        image = session.exec(
            select(ProductImage).where(
                ProductImage.product_id == item.product.id,
                ProductImage.is_default,
            )
        ).first()

        cart_items.append(
            ShoppingCartItemPublic(
                id=item.id,
                product_id=item.product.id,
                name=item.product.name,
                image_id=(image.id if image else None),
                price=item.product.price,
                stock_qty=item.product.stock_qty,
                cart_qty=item.qty,
            )
        )

    return ShoppingCartPublic(items=cart_items)


@router.get("/", response_model=ShoppingCartPublic, status_code=status.HTTP_200_OK)
def get_cart(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    cart = get_or_create_cart(session, current_user.id)
    return build_cart_public(session, cart)


@router.post(
    "/items", response_model=ShoppingCartPublic, status_code=status.HTTP_201_CREATED
)
def create_cart_item(
    *,
    shopping_cart_item_data: ShoppingCartItemCreateInCart,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if shopping_cart_item_data.qty < 1:
        raise HTTPException(
            status_code=400,
            detail={"errors": {"qty": "Quantity must be at least 1"}},
        )

    product = session.get(Product, shopping_cart_item_data.product_id)
    if product is None:
        raise HTTPException(
            status_code=400,
            detail={"errors": {"product_id": "Product not found"}},
        )

    cart = get_or_create_cart(session, current_user.id)

    shopping_cart_item = session.exec(
        select(ShoppingCartItem).where(
            ShoppingCartItem.shopping_cart_id == cart.id,
            ShoppingCartItem.product_id == shopping_cart_item_data.product_id,
        )
    ).first()

    if shopping_cart_item is None:
        shopping_cart_item = ShoppingCartItem(
            shopping_cart_id=cart.id,
            product_id=shopping_cart_item_data.product_id,
            qty=shopping_cart_item_data.qty,
        )
    else:
        raise HTTPException(
            status_code=409,
            detail={"errors": {"product_id": "This product is already in your cart"}},
        )

    session.add(shopping_cart_item)
    session.commit()
    session.refresh(cart)
    cart = get_or_create_cart(session, current_user.id)
    return build_cart_public(session, cart)


@router.delete("/items/{shopping_cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart_item(
    *,
    shopping_cart_item_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    cart = get_or_create_cart(session, current_user.id)
    shopping_cart_item = session.exec(
        select(ShoppingCartItem).where(
            ShoppingCartItem.id == shopping_cart_item_id,
            ShoppingCartItem.shopping_cart_id == cart.id,
        )
    ).first()
    if shopping_cart_item is None:
        raise HTTPException(
            status_code=404,
            detail={
                "errors": {
                    "shopping_cart_item_id": "Shopping cart item not found in cart"
                }
            },
        )

    session.delete(shopping_cart_item)
    session.commit()
    return None


@router.patch("/items/{shopping_cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_cart_item_qty(
    *,
    shopping_cart_item_id: int,
    shopping_cart_item_data: ShoppingCartItemUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if shopping_cart_item_data.qty < 1:
        raise HTTPException(
            status_code=400,
            detail={"errors": {"qty": "Quantity must be at least 1"}},
        )

    cart = get_or_create_cart(session, current_user.id)
    shopping_cart_item = session.exec(
        select(ShoppingCartItem).where(
            ShoppingCartItem.id == shopping_cart_item_id,
            ShoppingCartItem.shopping_cart_id == cart.id,
        )
    ).first()
    if shopping_cart_item is None:
        raise HTTPException(
            status_code=404,
            detail={
                "errors": {
                    "shopping_cart_item_id": "Shopping cart item not found in cart"
                }
            },
        )

    shopping_cart_item.qty = shopping_cart_item_data.qty
    session.add(shopping_cart_item)
    session.commit()
    return None


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart_items(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    cart = get_or_create_cart(session, current_user.id)
    session.exec(
        delete(ShoppingCartItem).where(ShoppingCartItem.shopping_cart_id == cart.id)
    )
    session.commit()
    return None


@router.post("/checkout", status_code=status.HTTP_201_CREATED)
def check_out(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    cart = get_or_create_cart(session, current_user.id)

    if not cart.items:
        raise HTTPException(
            status_code=400,
            detail={"errors": {"cart": "Shopping cart is empty"}},
        )

    stock_errors: dict[int, str] = {}
    locked_products: dict[int, Product] = {}
    for item in cart.items:
        product = session.exec(
            select(Product).where(Product.id == item.product_id).with_for_update()
        ).first()
        if product is None:
            stock_errors[item.product_id] = "Product not found"
            continue

        locked_products[item.product_id] = product

        if item.qty > product.stock_qty:
            stock_errors[item.product_id] = (
                f"Only {product.stock_qty} item(s) left in stock"
            )

    if stock_errors:
        raise HTTPException(
            status_code=409,
            detail={"errors": {"stock": stock_errors}},
        )

    product_ids = [item.product_id for item in cart.items]
    default_images = session.exec(
        select(ProductImage).where(
            ProductImage.product_id.in_(product_ids),
            ProductImage.is_default,
        )
    ).all()
    default_image_by_product_id = {img.product_id: img.id for img in default_images}
    order_nr = int(session.exec(text("SELECT nextval('orders_order_nr_seq')")).one()[0])

    for item in cart.items:
        product = locked_products[item.product_id]
        unit_price = product.price

        order_item = Order(
            order_nr=order_nr,
            user_id=current_user.id,
            product_id=product.id,
            qty=item.qty,
            unit_price=unit_price,
            line_total=unit_price * item.qty,
            product_name=product.name,
            product_sku=product.sku,
            default_image=default_image_by_product_id.get(product.id),
        )
        session.add(order_item)

        product.stock_qty -= item.qty
        session.add(product)

    session.exec(
        delete(ShoppingCartItem).where(ShoppingCartItem.shopping_cart_id == cart.id)
    )
    session.commit()
    return {"purchased_items": len(cart.items)}
