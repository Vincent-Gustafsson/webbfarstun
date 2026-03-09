import os

from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

from .products import models

DB_USERNAME = os.getenv("DB_USERNAME", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "webbfarstun")

DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

_engine = None


def get_engine():
    """Only create the engine when actually called."""
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL)
    return _engine


def create_db_and_tables():
    engine = get_engine()
    SQLModel.metadata.create_all(engine)

    # Lightweight schema patch for existing databases:
    # older deployments may already have "orders" without this newer snapshot field.
    with engine.begin() as conn:
        conn.execute(text("CREATE SEQUENCE IF NOT EXISTS orders_order_nr_seq"))
        conn.execute(
            text(
                "ALTER TABLE IF EXISTS orders ADD COLUMN IF NOT EXISTS order_nr BIGINT"
            )
        )
        conn.execute(
            text(
                "ALTER TABLE IF EXISTS orders "
                "ADD COLUMN IF NOT EXISTS default_image INTEGER"
            )
        )


def get_session():
    with Session(get_engine()) as session:
        yield session
