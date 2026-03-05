from datetime import datetime
from typing import Any, Dict

from pydantic import EmailStr
from pydantic_core.core_schema import bool_schema
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm.base import PASSIVE_NO_RESULT
from sqlalchemy.orm.state import PASSIVE_NO_INITIALIZE
from sqlalchemy.types import JSON
from sqlmodel import Field, SQLModel


class CategoryBase(SQLModel):
    name: str
    description: str | None = None
    category_parent_id: int | None = None
    is_container: bool = False


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(SQLModel):
    name: str | None
    description: str | None
    category_parent_id: int | None
    is_container: bool | None


class CategoryPublic(CategoryBase):
    id: int


class ProductBase(SQLModel):
    name: str
    product_group_id: int
    price: int
    stock_qty: int
    description: str
    sku: str | None = Field(default=None, unique=True)


class ProductCreate(ProductBase):
    options: list[int]


class ProductUpdate(SQLModel):
    name: str | None = None
    product_group_id: int | None = None
    price: int | None = None
    stock_qty: int | None = None
    description: str | None = None
    sku: str | None = None


class ProductPublic(ProductBase):
    id: int

    options: list[int] = Field(default_factory=list)
    variations: list["VariationDropdownPublic"] = Field(default_factory=list)

    product_images: list["ProductImagePublic"] = Field(
        default_factory=list,
        serialization_alias="images",
    )

    review_count: int = 0
    review_score: float = 0.0


class ProductListItem(SQLModel):
    id: int
    name: str
    price: int
    stock_qty: int
    sku: str | None = None
    description: str | None = None
    product_group_id: int
    category_id: int | None = None

    default_image: int | None = None

    options: list[int] = Field(default_factory=list)

    review_score: float = 0.0


class ProductGroupBase(SQLModel):
    name: str


class ProductGroupCreate(ProductGroupBase):
    category_id: int | None = None
    variation_ids: list[int] = []


class ProductGroupUpdate(ProductGroupBase):
    name: str | None = None
    category_id: int | None = None
    variation_ids: list[int] | None = None


class ProductGroupPublic(ProductGroupBase):
    id: int
    category_id: int
    variation_ids: list[int] = []


class VariationBase(SQLModel):
    name: str


class VariationCreate(VariationBase):
    category_id: int | None = None


class VariationUpdate(VariationBase):
    pass


class VariationPublic(VariationBase):
    id: int
    category_id: int | None = None


class VariationDropdownPublic(VariationPublic):
    options: list["VariationOptionPublic"] = Field(default_factory=list)
    selected_option_id: int | None = None


class VariationOptionBase(SQLModel):
    value: str


class VariationOptionCreate(VariationOptionBase):
    variation_id: int | None


class VariationOptionUpdate(VariationOptionBase):
    pass


class VariationOptionPublic(VariationOptionBase):
    id: int
    variation_id: int


class ProductConfigBase(SQLModel):
    pass


class ProductConfigCreate(ProductConfigBase):
    pass


class ProductConfigUpdate(ProductConfigBase):
    pass


class ProductConfigPublic(ProductConfigBase):
    variation_option_id: int
    product_id: int


class ProductGroupVariationBase(SQLModel):
    pass


class ProductGroupVariationCreate(ProductGroupVariationBase):
    pass


class ProductGroupVariationUpdate(ProductGroupVariationBase):
    pass


class ProductGroupVariationPublic(ProductGroupVariationBase):
    product_group_id: int
    variation_id: int


class ProductImageBase(SQLModel):
    is_default: bool


class ProductImageCreate(ProductImageBase):
    product_id: int


class ProductImageUpdate(ProductImageBase):
    pass


class ProductImagePublic(ProductImageBase):
    id: int
    product_id: int
    url: str


class UserBase(SQLModel):
    name: str
    password_hash: str
    is_admin: bool = False
    is_employee: bool = False
    is_active: bool = True


class UserPublic(SQLModel):
    id: int
    email: EmailStr
    name: str | None
    is_admin: bool
    is_employee: bool
    is_active: bool


class UserRegister(SQLModel):
    email: EmailStr
    password: str
    name: str | None = None


class UserUpdate(SQLModel):
    name: str | None = None
    is_admin: bool | None = None
    is_employee: bool | None = None
    is_active: bool | None = None


class ActionBase(SQLModel):
    type: str
    meta: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(
            # JSON everywhere, but JSONB on Postgres
            MutableDict.as_mutable(JSON().with_variant(JSONB, "postgresql")),
            nullable=False,
        ),
    )
    at_time: datetime


class ActionCreate(ActionBase):
    user_id: int


class ActionPublic(ActionBase):
    id: int
    user_id: int


class ActionUpdate(ActionBase): ...


class ReviewBase(SQLModel):
    score: int
    comment: str


class ReviewCreate(ReviewBase):
    product_group_id: int


class ReviewUser(SQLModel):
    name: str
    id: int


class ReviewPublic(ReviewBase):
    id: int
    product_group_id: int
    user: ReviewUser


class ShoppingCartItemBase(SQLModel):
    qty: int


class ShoppingCartItemCreate(ShoppingCartItemBase):
    product_id: int
    shopping_cart_id: int


class ShoppingCartItemCreateInCart(ShoppingCartItemBase):
    product_id: int


class ShoppingCartItemUpdate(SQLModel):
    qty: int


class ShoppingCartItemPublic(SQLModel):
    name: str
    image_id: int | None = None
    price: int
    stock_qty: int
    cart_qty: int
    id: int
    product_id: int


class ShoppingCartPublic(SQLModel):
    items: list[ShoppingCartItemPublic]


class TokenOut(SQLModel):
    access_token: str
    token_type: str = "bearer"
