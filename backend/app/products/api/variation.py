from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from ...db import get_session
from ..models import Category, Variation
from ..schemas import (
    VariationBase,
    VariationCreate,
    VariationPublic,
    VariationUpdate,
)

router = APIRouter(prefix="/variations", tags=["variations"])


@router.post("/", response_model=VariationPublic, status_code=status.HTTP_201_CREATED)
def create_variation(
    *, session: Session = Depends(get_session), variation_data: VariationCreate
):
    if not variation_data.category_id:
        raise HTTPException(status_code=400, detail="Category is required")

    category_exists = session.get(Category, variation_data.category_id)
    if not category_exists:
        raise HTTPException(status_code=400, detail="Category not found")

    db_variation = Variation.model_validate(variation_data)
    session.add(db_variation)
    session.commit()
    session.refresh(db_variation)
    return db_variation


@router.get("/", response_model=list[VariationPublic])
def get_variations(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    variation = session.exec(select(Variation).offset(offset).limit(limit)).all()
    return variation


@router.get("/{variation_id}", response_model=VariationPublic)
def get_variation(*, variation_id: int, session: Session = Depends(get_session)):
    variation = session.get(Variation, variation_id)
    if not variation:
        raise HTTPException(status_code=404, detail="Variation group not found")
    return variation


@router.patch("/{variation_id}", response_model=VariationUpdate)
def update_variation(
    *,
    variation_id: int,
    variation_data: VariationUpdate,
    session: Session = Depends(get_session),
):
    db_variation = session.get(Variation, variation_id)
    if not db_variation:
        raise HTTPException(status_code=404, detail="Product group not found")

    update_dict = variation_data.model_dump(exclude_unset=True)
    db_variation.sqlmodel_update(update_dict)

    session.add(db_variation)
    session.commit()
    session.refresh(db_variation)
    return db_variation


@router.delete("/{variation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_variation(*, variation_id: int, session: Session = Depends(get_session)):
    variation = session.get(Variation, variation_id)
    if not variation:
        raise HTTPException(status_code=404, detail="Product group not found")
    session.delete(variation)
    session.commit()
    return None
