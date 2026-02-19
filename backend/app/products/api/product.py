from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, col, select

from ...db import get_session
from ..models import Product, ProductGroup, VariationOption
from ..schemas import ProductCreate, ProductListItem, ProductPublic, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductPublic, status_code=status.HTTP_201_CREATED)
def create_product(
    *, session: Session = Depends(get_session), product_data: ProductCreate
):
    if not product_data.product_group_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": {"product_group_id": "Product group ID is required"}},
        )

    product_group_exists = session.get(ProductGroup, product_data.product_group_id)
    if not product_group_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": {"product_group_id": "Invalid product group ID"}},
        )

    existing = session.exec(
        select(Product).where(Product.sku == product_data.sku)
    ).first()

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": {"sku": "SKU already exists"}},
        )

    db_product = Product(**product_data.model_dump(exclude={"options"}))

    option_ids = list(dict.fromkeys(product_data.options or []))
    if option_ids:
        result = session.exec(
            select(VariationOption).where(VariationOption.id.in_(option_ids))
        ).all()

        get_all_options_ids = [option.id for option in result]
        check_if_all_options_exist = all(
            option_id in get_all_options_ids for option_id in option_ids
        )
        if not check_if_all_options_exist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"errors": {"options": "Invalid option IDs"}},
            )

        db_product.variation_options = result

    session.add(db_product)
    session.commit()

    db_product = session.exec(
        select(Product)
        .where(Product.id == db_product.id)
        .options(selectinload(Product.variation_options))
    ).one()

    return ProductPublic(
        **db_product.model_dump(),
        options=[option.id for option in db_product.variation_options],
    )


@router.get("/", response_model=list[ProductListItem])
def get_products(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    category_id: int | None = None,
):
    default_image_url = (
        select(ProductImage.url)
        .where(
            ProductImage.product_id == Product.id,
            ProductImage.is_default.is_(True),
        )
        .scalar_subquery()
    )

    stmt = (
        select(
            Product,
            ProductGroup.category_id,
            default_image_url.label("default_image"),
        )
        .join(ProductGroup, Product.product_group_id == ProductGroup.id)
        .options(selectinload(Product.variation_options))
        .offset(offset)
        .limit(limit)
    )

    if category_id is not None:
        stmt = stmt.where(ProductGroup.category_id == category_id)

    rows = session.exec(stmt).all()  # list[tuple[Product, int|None, str|None]]

    return [
        ProductListItem(
            id=p.id,
            name=p.name,
            price=p.price,
            stock_qty=p.stock_qty,
            sku=p.sku,
            product_group_id=p.product_group_id,
            category_id=cat_id,
            default_image=default_url,
            options=[o.id for o in p.variation_options],
        )
        for (p, cat_id, default_url) in rows
    ]


@router.get("/{product_id}", response_model=ProductPublic)
def get_product(*, product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=404, detail={"errors": {"product": "Product not found"}}
        )
    return product


@router.patch("/{product_id}", response_model=ProductUpdate)
def update_product(
    *,
    product_id: int,
    product_data: ProductUpdate,
    session: Session = Depends(get_session),
):
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(
            status_code=404, detail={"errors": {"category": "category not found"}}
        )

    update_dict = product_data.model_dump(exclude_unset=True)
    _ = db_product.sqlmodel_update(update_dict)

    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(*, product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=404, detail={"errors": {"product": "Product not found"}}
        )
    session.delete(product)
    session.commit()
    return None
