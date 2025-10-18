import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# --- Test Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Fixture for database setup/teardown ---
@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# --- Test Dependency Override ---
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client(test_db):
    """
    Yield a TestClient instance that uses the test_db fixture.
    """
    yield TestClient(app)


# --- Test Cases ---

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Hermes API"}

def test_create_category(client):
    response = client.post("/master/category", json={"name": "Groceries"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Groceries"
    assert "id" in data

def test_create_duplicate_category(client):
    # Create the category for the first time
    client.post("/master/category", json={"name": "Groceries"})
    # Try to create it again
    response = client.post("/master/category", json={"name": "Groceries"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Category already registered"}

def test_create_item(client):
    # First create a category and get its ID
    category_response = client.post("/master/category", json={"name": "Dairy"})
    assert category_response.status_code == 200
    category_data = category_response.json()
    category_id = category_data["id"]

    # Then create an item in that category using the retrieved ID
    response = client.post("/master/item", json={"name_standard": "Milk", "category_id": category_id})
    assert response.status_code == 200
    data = response.json()
    assert data["name_standard"] == "Milk"
    assert data["category"]["name"] == "Dairy"