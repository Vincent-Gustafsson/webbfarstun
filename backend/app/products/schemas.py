from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm.base import PASSIVE_NO_RESULT
from sqlalchemy.orm.state import PASSIVE_NO_INITIALIZE
from sqlmodel import Field, SQLModel


class CategoryBase(SQLModel):
    name: str
    description: str | None = None
    category_parent_id: int | None = None
    is_container: bool = False


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
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


class ProductUpdate(ProductBase):
    name: str | None = None
    product_group_id: int | None = None
    price: int | None = None
    stock_qty: int | None = None
    description: str | None = None
    sku: str | None = None


class ProductPublic(ProductBase):
    id: int
    options: list[int] = Field(default_factory=list)


class ProductGroupBase(SQLModel):
    name: str


class ProductGroupCreate(ProductGroupBase):
    category_id: int | None = None


class ProductGroupUpdate(ProductGroupBase):
    category_id: int | None = None


class ProductGroupPublic(ProductGroupBase):
    id: int
    category_id: int


class VariationBase(SQLModel):
    name: str


class VariationCreate(VariationBase):
    category_id: int | None = None


class VariationUpdate(VariationBase):
    pass


class VariationPublic(VariationBase):
    id: int
    category_id: int | None = None


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
    id: int
    variation_option_id: int
    product_id: int


class ProductImageBase(SQLModel):
    url: str


class ProductImageCreate(ProductImageBase):
    product_id: int


class ProductImageUpdate(ProductImageBase):
    pass


class ProductImagePublic(ProductImageBase):
    id: int
    product_id: int


class UserBase(SQLModel):
    name: str
    password_hash: str
    is_admin: bool = False
    is_employee: bool = False
    is_active: bool = True


class UserCreate(UserBase):
    email: str = Field(unique=True)


class UserPublic(UserBase):
    id: int
    email: str


class UserUpdate(UserBase):
    name: str | None = None
    password_hash: str | None = None
    is_admin: bool | None = None
    is_employee: bool | None = None
    is_active: bool | None = None


class ActionBase(SQLModel):
    type: str
    metadata: dict = Field(sa_type=JSONB)
    at_time: datetime


class ActionCreate(ActionBase):
    pass


class ActionPublic(ActionBase):
    id: int
    user_id: int


class ActionUpdate(ActionBase):
    type: str | None = None
    meta: dict | None = None
    at_time: datetime | None = None
