from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, delete, select

from ...db import get_session
from ..image_storage import delete_product_image_impl
from ..models import (
    Product,
    ProductConfig,
    ProductGroup,
    ProductImage,
    Review,
    ShoppingCartItem,
    Variation,
    VariationOption,
)
from ..schemas import (
    ProductCreate,
    ProductListItem,
    ProductPublic,
    ProductUpdate,
    VariationDropdownPublic,
    VariationOptionPublic,
)

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
        select(ProductImage.id)
        .where(ProductImage.product_id == Product.id, ProductImage.is_default.is_(True))
        .scalar_subquery()
    )

    avg_score_sq = (
        select(func.coalesce(func.avg(Review.score), 0.0))
        .where(Review.product_group_id == Product.product_group_id)
        .scalar_subquery()
    )

    stmt = (
        select(
            Product,
            ProductGroup.category_id,
            default_image_url.label("default_image"),
            avg_score_sq.label("review_score"),
        )
        .join(ProductGroup, Product.product_group_id == ProductGroup.id)
        .options(selectinload(Product.variation_options))
        .offset(offset)
        .limit(limit)
    )

    if category_id is not None:
        stmt = stmt.where(ProductGroup.category_id == category_id)

    rows = session.exec(stmt).all()

    return [
        ProductListItem(
            id=p.id,
            name=p.name,
            price=p.price,
            stock_qty=p.stock_qty,
            sku=p.sku,
            description=p.description,
            product_group_id=p.product_group_id,
            category_id=cat_id,
            default_image=default_img,
            options=[o.id for o in p.variation_options],
            review_score=round(float(review_score or 0.0), 1),
        )
        for (p, cat_id, default_img, review_score) in rows
    ]


@router.get("/{product_id}", response_model=ProductPublic)
def get_product(*, product_id: int, session: Session = Depends(get_session)):
    stmt = (
        select(Product)
        .where(Product.id == product_id)
        .options(
            selectinload(Product.product_images),
            selectinload(Product.variation_options),
            selectinload(Product.product_group)
            .selectinload(ProductGroup.variations)
            .selectinload(Variation.variation_options),
        )
    )
    product = session.exec(stmt).one_or_none()
    if not product:
        raise HTTPException(
            status_code=404, detail={"errors": {"product": "Product not found"}}
        )

    # aggregates for this product's group
    review_count, avg_score = session.exec(
        select(func.count(Review.id), func.avg(Review.score)).where(
            Review.product_group_id == product.product_group_id
        )
    ).one()

    review_score = round(float(avg_score or 0.0), 1)

    selected_by_variation = {
        opt.variation_id: opt.id for opt in product.variation_options
    }

    variations_payload = []
    for v in product.product_group.variations if product.product_group else []:
        variations_payload.append(
            VariationDropdownPublic(
                id=v.id,
                name=v.name,
                category_id=v.category_id,
                options=[
                    VariationOptionPublic(
                        id=o.id, variation_id=o.variation_id, value=o.value
                    )
                    for o in v.variation_options
                ],
                selected_option_id=selected_by_variation.get(v.id),
            )
        )

    base = product.model_dump(exclude={"product_images", "variation_options"})
    return ProductPublic(
        **base,
        options=[o.id for o in product.variation_options],
        product_images=product.product_images,
        variations=variations_payload,
        review_count=review_count,
        review_score=review_score,
    )


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

    try:
        images = session.exec(
            select(ProductImage).where(ProductImage.product_id == product_id)
        ).all()
        for img in images:
            delete_product_image_impl(session, img)

        session.exec(
            delete(ShoppingCartItem).where(ShoppingCartItem.product_id == product_id)
        )
        session.exec(
            delete(ProductConfig).where(ProductConfig.product_id == product_id)
        )

        session.delete(product)
        session.commit()
        return None

    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail={
                "errors": {
                    "product": "Cannot delete product due to existing references"
                }
            },
        )
