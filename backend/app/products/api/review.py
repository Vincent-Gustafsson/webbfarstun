from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from ...auth.deps import get_current_user
from ...db import get_session
from ..models import ProductGroup, Review, User
from ..schemas import ReviewCreate, ReviewPublic

router = APIRouter(prefix="/reviews", tags=["reviews"])
product_reviews_router = APIRouter(prefix="/products", tags=["reviews"])


@router.post("/", response_model=ReviewPublic, status_code=status.HTTP_201_CREATED)
def create_review(
    *,
    session: Session = Depends(get_session),
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
):
    if not session.get(ProductGroup, review_data.product_group_id):
        raise HTTPException(
            status_code=400,
            detail={"errors": {"product_group_id": "Product group not found"}},
        )

    db_review = Review.model_validate(
        {**review_data.model_dump(), "user_id": current_user.id}
    )

    session.add(db_review)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have a review for this product",
        )

    session.refresh(db_review)
    return db_review


@product_reviews_router.get(
    "/{product_group_id}/reviews", response_model=list[ReviewPublic]
)
def get_reviews_for_product_group(
    product_group_id: int,
    *,
    session: Session = Depends(get_session),
):
    if not session.get(ProductGroup, product_group_id):
        raise HTTPException(
            status_code=404,
            detail={"errors": {"product_group_id": "Product group not found"}},
        )

    stmt = select(Review).where(Review.product_group_id == product_group_id)
    return session.exec(stmt).all()


@router.get("/{review_id}", response_model=ReviewPublic)
def get_review(*, review_id: int, session: Session = Depends(get_session)):
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(
            status_code=404, detail={"errors": {"review_id": "Review not found"}}
        )
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    *,
    review_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(
            status_code=404, detail={"errors": {"review_id": "Review not found"}}
        )

    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"errors": {"review": "You can only delete your own review"}},
        )

    session.delete(review)
    session.commit()
    return None
