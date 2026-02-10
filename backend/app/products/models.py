from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from .schemas import (
    ActionBase,
    CategoryBase,
    ProductBase,
    ProductConfigBase,
    ProductGroupBase,
    ProductImageBase,
    UserBase,
    VariationBase,
    VariationOptionBase,
)


class Category(CategoryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    category_parent_id: int | None = Field(default=None, foreign_key="category.id")
    parent: Optional["Category"] = Relationship(
        back_populates="subcategories",
        sa_relationship_kwargs={"remote_side": "Category.id"},
    )
    subcategories: list["Category"] = Relationship(
        back_populates="parent",
        cascade_delete=True,
    )
    product_groups: list["ProductGroup"] = Relationship(back_populates="category")
    variations: list["Variation"] = Relationship(back_populates="category")


class ProductConfig(ProductConfigBase, table=True):
    variation_option_id: int = Field(foreign_key="variationoption.id", primary_key=True)
    product_id: int = Field(foreign_key="product.id", primary_key=True)


class Product(ProductBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    product_group_id: int = Field(foreign_key="productgroup.id")
    product_group: "ProductGroup" = Relationship(back_populates="products")
    product_images: list["ProductImage"] = Relationship(back_populates="product")
    variation_options: list["VariationOption"] = Relationship(
        back_populates="products", link_model=ProductConfig
    )


class ProductGroup(ProductGroupBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="category.id")
    products: list["Product"] = Relationship(back_populates="product_group")
    category: "Category" = Relationship(back_populates="product_groups")


class Variation(VariationBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="category.id")
    category: "Category" = Relationship(back_populates="variations")
    variation_options: list["VariationOption"] = Relationship(
        back_populates="variation"
    )


class VariationOption(VariationOptionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    variation_id: int = Field(foreign_key="variation.id")
    variation: "Variation" = Relationship(back_populates="variation_options")
    products: list["Product"] = Relationship(
        back_populates="variation_options", link_model=ProductConfig
    )


class ProductImage(ProductImageBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    product: Product = Relationship(back_populates="product_images")


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    action: list["Action"] = Relationship(back_populates="user")


class Action(ActionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="action")
