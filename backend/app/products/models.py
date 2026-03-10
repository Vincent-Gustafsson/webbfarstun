from typing import Optional

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Index, Relationship, SQLModel, UniqueConstraint, text

from .schemas import (
    ActionBase,
    CategoryBase,
    OrderBase,
    ProductBase,
    ProductConfigBase,
    ProductGroupBase,
    ProductGroupVariationBase,
    ProductImageBase,
    ReviewBase,
    ShoppingCartItemBase,
    UserBase,
    VariationBase,
    VariationOptionBase,
)


class Category(CategoryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    category_parent_id: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("category.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    parent: Optional["Category"] = Relationship(
        back_populates="subcategories",
        sa_relationship_kwargs={"remote_side": "Category.id"},
    )
    subcategories: list["Category"] = Relationship(
        back_populates="parent",
        cascade_delete=True,
    )
    product_groups: list["ProductGroup"] = Relationship(
        back_populates="category",
        sa_relationship_kwargs={"passive_deletes": True},
    )
    variations: list["Variation"] = Relationship(
        back_populates="category",
        sa_relationship_kwargs={"passive_deletes": True},
    )


class ProductConfig(ProductConfigBase, table=True):
    variation_option_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("variationoption.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )
    product_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("product.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )


class Product(ProductBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    product_group: "ProductGroup" = Relationship(back_populates="products")
    product_images: list["ProductImage"] = Relationship(back_populates="product")
    shopping_cart_items: list["ShoppingCartItem"] = Relationship(
        back_populates="product"
    )
    variation_options: list["VariationOption"] = Relationship(
        back_populates="products", link_model=ProductConfig
    )
    product_group_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("productgroup.id", ondelete="CASCADE"),
            nullable=False,
        )
    )


class ProductGroupVariation(ProductGroupVariationBase, table=True):
    product_group_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("productgroup.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )
    variation_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("variation.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )


class ProductGroup(ProductGroupBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    category_id: int = Field(
        sa_column=Column(Integer, ForeignKey("category.id", ondelete="CASCADE"))
    )
    category: "Category" = Relationship(back_populates="product_groups")
    products: list["Product"] = Relationship(
        back_populates="product_group",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )

    reviews: list["Review"] = Relationship(
        back_populates="product_group",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )

    variations: list["Variation"] = Relationship(
        back_populates="product_groups",
        link_model=ProductGroupVariation,
    )


class Variation(VariationBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    category_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("category.id", ondelete="CASCADE"),
        )
    )
    category: "Category" = Relationship(back_populates="variations")
    variation_options: list["VariationOption"] = Relationship(
        back_populates="variation"
    )
    product_groups: list["ProductGroup"] = Relationship(
        back_populates="variations", link_model=ProductGroupVariation
    )


class VariationOption(VariationOptionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    variation_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("variation.id", ondelete="CASCADE"),
        )
    )
    variation: "Variation" = Relationship(back_populates="variation_options")
    products: list["Product"] = Relationship(
        back_populates="variation_options", link_model=ProductConfig
    )


class ProductImage(ProductImageBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("product.id", ondelete="CASCADE"),
        )
    )
    product: Product = Relationship(back_populates="product_images")

    url: str
    is_default: bool = Field(default=False, nullable=False)

    __table_args__ = (
        # Only ONE row per product is allowed to have is_default = true
        Index(
            "uq_product_one_default_image",
            "product_id",
            unique=True,
            postgresql_where=text("is_default IS TRUE"),
            sqlite_where=text("is_default = 1"),
        ),
    )


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    actions: list["Action"] = Relationship(back_populates="user")
    reviews: list["Review"] = Relationship(back_populates="user")
    shopping_cart: Optional["ShoppingCart"] = Relationship(back_populates="user")
    orders: list["Order"] = Relationship(back_populates="user")


class Action(ActionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="actions")


class Review(ReviewBase, table=True):
    __table_args__ = (
        UniqueConstraint(
            "user_id", "product_group_id", name="uq_review_user_product_group"
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    product_group_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("productgroup.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    user_id: int = Field(foreign_key="user.id")
    product_group: "ProductGroup" = Relationship(back_populates="reviews")
    user: "User" = Relationship(back_populates="reviews")


class ShoppingCart(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    user: "User" = Relationship(back_populates="shopping_cart")
    items: list["ShoppingCartItem"] = Relationship(back_populates="shopping_cart")


class ShoppingCartItem(ShoppingCartItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("product.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    shopping_cart_id: int = Field(foreign_key="shoppingcart.id")
    product: "Product" = Relationship(back_populates="shopping_cart_items")
    shopping_cart: "ShoppingCart" = Relationship(back_populates="items")


class Order(OrderBase, table=True):
    __tablename__ = "orders"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
        )
    )

    user: "User" = Relationship(back_populates="orders")
