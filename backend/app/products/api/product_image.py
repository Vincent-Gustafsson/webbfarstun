from app.db import get_session
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from ..image_storage import resolve_media_path, save_product_image
from ..models import Product, ProductImage
from ..schemas import (
    ProductImageBase,
    ProductImageCreate,
    ProductImagePublic,
    ProductImageUpdate,
)

router = APIRouter(prefix="/product-images", tags=["product-images"])


@router.post(
    "/", response_model=ProductImagePublic, status_code=status.HTTP_201_CREATED
)
def create_product_image(
    *, session: Session = Depends(get_session), product_image_data: ProductImageCreate
):
    if not product_image_data.product_id:
        raise HTTPException(
            status_code=400, detail={"errors": {"product_id": "Product id is required"}}
        )

    product_exists = session.get(Product, product_image_data.product_id)
    if not product_exists:
        raise HTTPException(
            status_code=400, detail={"errors": {"product_id": "Product id not found"}}
        )

    db_product_image = ProductImage.model_validate(product_image_data)
    session.add(db_product_image)
    session.commit()
    session.refresh(db_product_image)
    return db_product_image


@router.get("/", response_model=list[ProductImagePublic])
def get_product_images(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    product_images = session.exec(
        select(ProductImage).offset(offset).limit(limit)
    ).all()
    return product_images


@router.get("/{product_image_id}", response_model=ProductImagePublic)
def get_product_image(
    *, product_image_id: int, session: Session = Depends(get_session)
):
    product_image = session.get(ProductImage, product_image_id)
    if not product_image:
        raise HTTPException(
            status_code=404,
            detail={"errors": {"product_image_id": "product image not found"}},
        )
    return product_image


@router.patch("/{product_image_id}", response_model=ProductImageUpdate)
def update_product_image(
    *,
    product_image_id: int,
    product_image_data: ProductImageUpdate,
    session: Session = Depends(get_session),
):
    db_product_image = session.get(ProductImage, product_image_id)
    if not db_product_image:
        raise HTTPException(
            status_code=404,
            detail={"errors": {"product_image_id": "product image not found"}},
        )

    update_dict = product_image_data.model_dump(exclude_unset=True)
    db_product_image.sqlmodel_update(update_dict)

    session.add(db_product_image)
    session.commit()
    session.refresh(db_product_image)
    return db_product_image


@router.delete("/{product_image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_image(
    *, product_image_id: int, session: Session = Depends(get_session)
):
    product_image = session.get(ProductImage, product_image_id)
    if not product_image:
        raise HTTPException(
            status_code=404,
            detail={"errors": {"product_image_id": "product image not found"}},
        )
    session.delete(product_image)
    session.commit()
    return None


@router.post(
    "/upload", response_model=ProductImagePublic, status_code=status.HTTP_201_CREATED
)
def upload_product_image(
    *,
    session: Session = Depends(get_session),
    product_id: int = Form(...),
    is_default: bool = Form(False),
    image: UploadFile = File(...),
):
    product_exists = session.get(Product, product_id)
    if not product_exists:
        raise HTTPException(
            status_code=400, detail={"errors": {"product_id": "Product id not found"}}
        )

    db_url = save_product_image(image)

    # Assumes ProductImageBase has "url: str"
    db_product_image = ProductImage(
        product_id=product_id, url=db_url, is_default=is_default
    )

    session.add(db_product_image)
    session.commit()
    session.refresh(db_product_image)
    return db_product_image


@router.get("/{product_image_id}/file")
def download_product_image_file(
    *, product_image_id: int, session: Session = Depends(get_session)
):
    product_image = session.get(ProductImage, product_image_id)
    if not product_image:
        raise HTTPException(
            status_code=404,
            detail={"errors": {"product_image_id": "product image not found"}},
        )

    abs_path = resolve_media_path(product_image.url)
    if not abs_path.exists():
        raise HTTPException(status_code=404, detail="Image file not found on disk")

    return FileResponse(abs_path)
