from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from ...db import get_session
from ..models import Category
from ..schemas import CategoryCreate, CategoryPublic, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryPublic, status_code=status.HTTP_201_CREATED)
def create_category(
    *, session: Session = Depends(get_session), category_data: CategoryCreate
):
    if category_data.category_parent_id:
        if not session.get(Category, category_data.category_parent_id):
            raise HTTPException(status_code=400, detail="Parent category not found")

    db_category = Category.model_validate(category_data)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


@router.get("/", response_model=list[CategoryPublic])
def get_categories(
    *,
    session: Session = Depends(get_session),
):
    categories = session.exec(select(Category)).all()
    return categories


@router.get("/{category_id}", response_model=CategoryPublic)
def get_category(*, category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get("/{category_id}/subcategories", response_model=list[CategoryPublic])
def get_subcategories(*, category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category.subcategories


@router.patch("/{category_id}", response_model=CategoryPublic)
def update_category(
    *,
    category_id: int,
    category_data: CategoryUpdate,
    session: Session = Depends(get_session),
):
    db_category = session.get(Category, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    update_dict = category_data.model_dump(exclude_unset=True)
    db_category.sqlmodel_update(update_dict)

    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(*, category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(category)
    session.commit()
    return None
