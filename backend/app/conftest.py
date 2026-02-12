from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from .db import get_session
from .main import app

# --- SQLite Setup for Tests ---
sqlite_url = "sqlite:///:memory:"

engine_test = create_engine(
    sqlite_url,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine_test)
    with Session(engine_test) as session:
        yield session
    SQLModel.metadata.drop_all(engine_test)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    # Make sure this patch path matches where 'create_db_and_tables' is IMPORTED in main.py
    # If main.py does "from .db import create_db_and_tables", patch "app.main.create_db_and_tables"
    with patch("app.main.create_db_and_tables"):
        client = TestClient(app)
        yield client

    app.dependency_overrides.clear()
