import pytest

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Hermes API"}

def test_create_category(client):
    response = client.post("/master/category", json={"name": "Abarrotes"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Abarrotes"
    assert "id" in data

def test_create_duplicate_category(client):
    # The seeded "Lácteos" category should exist from the conftest fixture
    response = client.post("/master/category", json={"name": "Lácteos"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Category already registered"}

def test_create_item(client):
    # Get the ID of a seeded category
    category_response = client.get("/master/categories")
    dairy_category = next(c for c in category_response.json() if c["name"] == "Lácteos")
    category_id = dairy_category["id"]

    # Then create an item in that category
    response = client.post("/master/item", json={"name_standard": "Milk", "category_id": category_id})
    assert response.status_code == 200
    data = response.json()
    assert data["name_standard"] == "Milk"
    assert data["category"]["name"] == "Lácteos"