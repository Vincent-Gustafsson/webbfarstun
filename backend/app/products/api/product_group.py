from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
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
    try:
        session.delete(product_group)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail={
                "errors": {
                    "product_group_id": "Cannot delete: referenced by other data."
                }
            },
        )

    return None


from sqlalchemy import Integer, bindparam, text
from sqlalchemy.dialects.postgresql import ARRAY

AVAILABILITY_NAMED_SQL = text("""
WITH group_variations AS (
  SELECT v.id AS variation_id
  FROM productgroupvariation pgv
  JOIN variation v ON v.id = pgv.variation_id
  WHERE pgv.product_group_id = :group_id
),
selected AS (
  SELECT vo.variation_id, vo.id AS option_id
  FROM variationoption vo
  JOIN group_variations gv ON gv.variation_id = vo.variation_id
  WHERE vo.id = ANY(:selected_option_ids)
),
group_options AS (
  SELECT vo.variation_id, vo.id AS option_id
  FROM variationoption vo
  JOIN group_variations gv ON gv.variation_id = vo.variation_id
)
SELECT
  v.id   AS variation_id,
  v.name AS variation_name,
  vo.id  AS option_id,
  vo.value AS option_value,
  EXISTS (
    SELECT 1
    FROM product p
    JOIN productconfig pc_opt
      ON pc_opt.product_id = p.id
     AND pc_opt.variation_option_id = vo.id
    WHERE p.product_group_id = :group_id
      AND NOT EXISTS (
        SELECT 1
        FROM selected s
        WHERE s.variation_id <> vo.variation_id
          AND NOT EXISTS (
            SELECT 1
            FROM productconfig pc_req
            WHERE pc_req.product_id = p.id
              AND pc_req.variation_option_id = s.option_id
          )
      )
  ) AS available
FROM group_options go
JOIN variation v       ON v.id = go.variation_id
JOIN variationoption vo ON vo.id = go.option_id
ORDER BY v.id, vo.id
""").bindparams(bindparam("selected_option_ids", type_=ARRAY(Integer)))

from typing import List, Optional

from pydantic import BaseModel


class AvailabilityRequest(BaseModel):
    selected_option_ids: List[int] = []


class OptionAvailability(BaseModel):
    variation_id: int
    option_id: int
    available: bool


class ResolveRequest(BaseModel):
    selected_option_ids: List[int]


class ResolveResponse(BaseModel):
    product_id: Optional[int]


class OptionAvailabilityNamed(BaseModel):
    variation_id: int
    variation_name: str
    option_id: int
    option_value: str
    available: bool


@router.post("/{group_id}/availability", response_model=list[OptionAvailabilityNamed])
def option_availability_named(
    group_id: int,
    body: AvailabilityRequest,
    session: Session = Depends(get_session),
):
    rows = session.exec(
        AVAILABILITY_NAMED_SQL,
        params={"group_id": group_id, "selected_option_ids": body.selected_option_ids},
    ).all()

    return [
        OptionAvailabilityNamed(
            variation_id=r[0],
            variation_name=r[1],
            option_id=r[2],
            option_value=r[3],
            available=bool(r[4]),
        )
        for r in rows
    ]


RESOLVE_SQL = text("""
WITH var_count AS (
  SELECT COUNT(*)::int AS n
  FROM productgroupvariation
  WHERE product_group_id = :group_id
),
selected AS (
  -- keep only selected options that belong to this product group (via variation membership)
  SELECT vo.variation_id, vo.id AS option_id
  FROM variationoption vo
  JOIN productgroupvariation pgv
    ON pgv.variation_id = vo.variation_id
  WHERE pgv.product_group_id = :group_id
    AND vo.id = ANY(:selected_option_ids)
),
wanted AS (
  SELECT
    array_agg(option_id ORDER BY variation_id) AS opts,
    COUNT(*)::int AS c,
    COUNT(DISTINCT variation_id)::int AS dc
  FROM selected
)
SELECT p.id
FROM product p
JOIN productconfig pc ON pc.product_id = p.id
JOIN variationoption vo ON vo.id = pc.variation_option_id
CROSS JOIN var_count vc
CROSS JOIN wanted w
WHERE p.product_group_id = :group_id
  -- require complete selection: one option per variation
  AND w.c  = vc.n
  AND w.dc = vc.n
GROUP BY p.id, w.opts
HAVING array_agg(vo.id ORDER BY vo.variation_id) = w.opts
LIMIT 1
""").bindparams(bindparam("selected_option_ids", type_=ARRAY(Integer)))


@router.post("/{group_id}/resolve", response_model=ResolveResponse)
def resolve_product(
    group_id: int,
    body: ResolveRequest,
    session: Session = Depends(get_session),
):
    row = session.exec(
        RESOLVE_SQL,
        params={"group_id": group_id, "selected_option_ids": body.selected_option_ids},
    ).first()

    # row is (id,) or None
    return ResolveResponse(product_id=row[0] if row else None)
