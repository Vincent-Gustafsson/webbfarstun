from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from ...db import get_session
from ..models import Category, Product, ProductGroup, ProductGroupVariation, Variation
from ..schemas import (
    ProductGroupBase,
    ProductGroupCreate,
    ProductGroupPublic,
    ProductGroupUpdate,
)

router = APIRouter(prefix="/product-groups", tags=["product-groups"])


@router.post(
    "/", response_model=ProductGroupPublic, status_code=status.HTTP_201_CREATED
)
def create_product_group(
    *, session: Session = Depends(get_session), product_data: ProductGroupCreate
):
    if not product_data.category_id:
        raise HTTPException(
            status_code=400,
            detail={"errors": {"category_id": "Category ID is required"}},
        )

    category_exists = session.get(Category, product_data.category_id)
    if not category_exists:
        raise HTTPException(
            status_code=400, detail={"errors": {"category_id": "Category ID not found"}}
        )

    db_product_group = ProductGroup(
        name=product_data.name, category_id=product_data.category_id
    )
    session.add(db_product_group)
    session.commit()
    session.refresh(db_product_group)

    variation_ids = list(dict.fromkeys(product_data.variation_ids))

    if variation_ids:
        variations = session.exec(
            select(Variation).where(Variation.id.in_(variation_ids))
        ).all()

        if len(variations) != len(variation_ids):
            raise HTTPException(
                400,
                detail={
                    "errors": {"variation_ids": "One or more variations not found"}
                },
            )

        if any(v.category_id != db_product_group.category_id for v in variations):
            raise HTTPException(
                400,
                detail={
                    "errors": {
                        "variation_ids": "Variations must belong to the selected category"
                    }
                },
            )

        session.add_all(
            [
                ProductGroupVariation(
                    product_group_id=db_product_group.id, variation_id=vid
                )
                for vid in variation_ids
            ]
        )
        session.commit()

    return db_product_group


@router.get("/", response_model=list[ProductGroupPublic])
def get_product_groups(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    product_groups = session.exec(
        select(ProductGroup)
        .options(selectinload(ProductGroup.variations))
        .offset(offset)
        .limit(limit)
    ).all()

    return [
        ProductGroupPublic(
            id=pg.id,
            name=pg.name,
            category_id=pg.category_id,
            variation_ids=[v.id for v in pg.variations if v.id is not None],
        )
        for pg in product_groups
    ]


@router.get("/{product_group_id}", response_model=ProductGroupPublic)
def get_product_group(
    *, product_group_id: int, session: Session = Depends(get_session)
):
    pg = session.exec(
        select(ProductGroup)
        .where(ProductGroup.id == product_group_id)
        .options(selectinload(ProductGroup.variations))
    ).first()

    if not pg:
        raise HTTPException(
            404, detail={"errors": {"product_group_id": "Product group not found"}}
        )

    return ProductGroupPublic(
        id=pg.id,
        name=pg.name,
        category_id=pg.category_id,
        variation_ids=[v.id for v in pg.variations if v.id is not None],
    )


@router.patch("/{product_group_id}", response_model=ProductGroupUpdate)
def update_product_group(
    *,
    product_group_id: int,
    product_group_data: ProductGroupUpdate,
    session: Session = Depends(get_session),
):
    db_product_group = session.get(ProductGroup, product_group_id)
    if not db_product_group:
        raise HTTPException(
            status_code=404,
            detail={"errors": {"product_group_id": "Product group not found"}},
        )

    update_dict = product_group_data.model_dump(exclude_unset=True)
    db_product_group.sqlmodel_update(update_dict)

    session.add(db_product_group)
    session.commit()
    session.refresh(db_product_group)
    return db_product_group


@router.delete("/{product_group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(*, product_group_id: int, session: Session = Depends(get_session)):
    product_group = session.get(ProductGroup, product_group_id)
    if not product_group:
        raise HTTPException(
            status_code=404,
            detail={"errors": {"product_group_id": "Product group not found"}},
        )
    session.delete(product_group)
    session.commit()
    return None
