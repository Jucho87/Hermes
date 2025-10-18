import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app import crud
from app.schemas.schemas import CategoryCreate

# --- Test Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency for all tests
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def db_session():
    # Create all tables before each test
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    # Seed initial categories for testing auto-classification
    try:
        categories_to_seed = ["Lácteos", "Panadería", "Bebidas", "Carnes", "Frutas y Verduras"]
        for category_name in categories_to_seed:
            category = crud.get_category_by_name(db, name=category_name)
            if not category:
                crud.create_category(db, category=CategoryCreate(name=category_name))

        yield db # This is the database session that the test will use

    finally:
        db.close()
        # Drop all tables after each test to ensure isolation
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """
    A fixture that provides a TestClient and ensures the db_session fixture is run.
    """
    yield TestClient(app)