from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from ...db import get_session
from ..models import Variation, VariationOption
from ..schemas import (
    VariationOptionCreate,
    VariationOptionPublic,
    VariationOptionUpdate,
)

router = APIRouter(prefix="/variation-options", tags=["variation-options"])


@router.post(
    "/", response_model=VariationOptionPublic, status_code=status.HTTP_201_CREATED
)
def create_variation_option(
    *, session: Session = Depends(get_session), v_opt_data: VariationOptionCreate
):
    if not session.get(Variation, v_opt_data.variation_id):
        raise HTTPException(
            status_code=400, detail={"errors": {"variation_id": "Variation not found"}}
        )

    check_variation_exists = session.exec(
        select(Variation).where(Variation.id == v_opt_data.variation_id)
    ).first()
    if not check_variation_exists:
        raise HTTPException(
            status_code=400, detail={"errors": {"variation_id": "Variation not found"}}
        )

    db_variation = VariationOption.model_validate(v_opt_data)
    session.add(db_variation)
    session.commit()
    session.refresh(db_variation)
    return db_variation


@router.get("/", response_model=list[VariationOptionPublic])
def get_varition_options(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    v_opts = session.exec(select(VariationOption).offset(offset).limit(limit)).all()
    return v_opts


@router.get("/{variation_option_id}", response_model=VariationOptionPublic)
def get_variation_option(
    *, variation_option_id: int, session: Session = Depends(get_session)
):
    v_opt = session.get(VariationOption, variation_option_id)
    if not v_opt:
        raise HTTPException(
            status_code=404,
            detail={"errors": {"variation_option_id": "variation option not found"}},
        )
    return v_opt


@router.patch("/{variation_option_id}", response_model=VariationOptionUpdate)
def update_variation_option(
    *,
    variation_option_id: int,
    v_opt_data: VariationOptionUpdate,
    session: Session = Depends(get_session),
):
    v_opt = session.get(VariationOption, variation_option_id)
    if not v_opt:
        raise HTTPException(
            status_code=404,
            detail={"errors": {"variation_option_id": "variation option not found"}},
        )

    update_dict = v_opt_data.model_dump(exclude_unset=True)
    _ = v_opt.sqlmodel_update(update_dict)

    session.add(v_opt)
    session.commit()
    session.refresh(v_opt)
    return v_opt


@router.delete("/{variation_option_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_variation_option(
    *, variation_option_id: int, session: Session = Depends(get_session)
):
    v_opt = session.get(VariationOption, variation_option_id)
    if not v_opt:
        raise HTTPException(
            status_code=404,
            detail={"errors": {"variation_option_id": "variation option not found"}},
        )
    session.delete(v_opt)
    session.commit()
    return None
