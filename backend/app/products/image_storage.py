from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlmodel import Session

from .models import ProductImage

BASE_DIR = Path(__file__).resolve().parents[2]
MEDIA_ROOT = BASE_DIR / "media"
PRODUCTS_DIR = MEDIA_ROOT / "products"

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}

MAX_BYTES = 10 * 1024 * 1024  # 10MB


def save_product_image(upload: UploadFile) -> str:
    """
    Saves the uploaded image to: backend/media/products/<uuid>.<ext>
    Returns the DB value: "products/<uuid>.<ext>"
    """
    if upload.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    ext = ALLOWED_CONTENT_TYPES[upload.content_type]
    filename = f"{uuid.uuid4().hex}.{ext}"

    PRODUCTS_DIR.mkdir(parents=True, exist_ok=True)

    abs_path = PRODUCTS_DIR / filename

    # Stream to disk and enforce a size limit
    written = 0
    with abs_path.open("wb") as f:
        while True:
            chunk = upload.file.read(1024 * 1024)  # 1MB chunks
            if not chunk:
                break
            written += len(chunk)
            if written > MAX_BYTES:
                abs_path.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="File too large")
            f.write(chunk)

    return f"products/{filename}"


def resolve_media_path(db_url: str) -> Path:
    """
    Takes DB value like "products/<file>" and returns absolute path safely.
    Prevents ../../ path tricks.
    """
    rel = Path(db_url)

    if rel.is_absolute() or ".." in rel.parts:
        raise HTTPException(status_code=400, detail="Invalid image path")

    abs_path = (MEDIA_ROOT / rel).resolve()
    media_root = MEDIA_ROOT.resolve()

    if media_root not in abs_path.parents and abs_path != media_root:
        raise HTTPException(status_code=400, detail="Invalid image path")

    return abs_path


def delete_product_image_impl(session: Session, product_image: ProductImage) -> None:
    if product_image.url:
        abs_path = resolve_media_path(product_image.url)
        if abs_path.exists():
            try:
                abs_path.unlink()
            except OSError:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to remove image file from disk",
                )

    session.delete(product_image)
