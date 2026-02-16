from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from ...db import get_session
from ..models import ProductGroup, Review, User
from ..schemas import ReviewCreate, ReviewPublic, ReviewUpdate

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewPublic, status_code=status.HTTP_201_CREATED)
def create_review(
    *, session: Session = Depends(get_session), review_data: ReviewCreate
):
    if not session.get(ProductGroup, review_data.product_group_id):
        raise HTTPException(
            status_code=400,
            detail={"errors": {"product_group_id": "Product group not found"}},
        )
    if not session.get(User, review_data.user_id):
        raise HTTPException(
            status_code=400, detail={"errors": {"user_id": "User not found"}}
        )

    db_review = Review.model_validate(review_data)
    session.add(db_review)
    session.commit()
    session.refresh(db_review)
    return db_review


@router.get("/", response_model=list[ReviewPublic])
def get_reviews(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    reviews = session.exec(select(Review).offset(offset).limit(limit)).all()
    return reviews


@router.get("/{review_id}", response_model=ReviewPublic)
def get_review(*, review_id: int, session: Session = Depends(get_session)):
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(
            status_code=404, detail={"errors": {"review_id": "Review not found"}}
        )
    return review


@router.patch("/{review_id}", response_model=ReviewPublic)
def update_review(
    *,
    review_id: int,
    review_data: ReviewUpdate,
    session: Session = Depends(get_session),
):
    db_review = session.get(Review, review_id)
    if not db_review:
        raise HTTPException(
            status_code=404, detail={"errors": {"review_id": "Review not found"}}
        )

    update_dict = review_data.model_dump(exclude_unset=True)

    if "product_group_id" in update_dict and not session.get(
        ProductGroup, update_dict["product_group_id"]
    ):
        raise HTTPException(
            status_code=400,
            detail={"errors": {"product_group_id": "Product group not found"}},
        )

    if "user_id" in update_dict and not session.get(User, update_dict["user_id"]):
        raise HTTPException(
            status_code=400, detail={"errors": {"user_id": "User not found"}}
        )

    db_review.sqlmodel_update(update_dict)
    session.add(db_review)
    session.commit()
    session.refresh(db_review)
    return db_review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(*, review_id: int, session: Session = Depends(get_session)):
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(
            status_code=404, detail={"errors": {"review_id": "Review not found"}}
        )
    session.delete(review)
    session.commit()
    return None
