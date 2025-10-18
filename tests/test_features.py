import pytest
from app.nlp import parse_shopping_list_text

# --- NLP Parsing Tests ---
def test_parse_simple_list():
    text = "2 leches, 1 pan"
    result = parse_shopping_list_text(text)
    assert len(result) == 2
    assert result[0] == {"quantity": "2", "name": "leches", "price": None}
    assert result[1] == {"quantity": "1", "name": "pan", "price": None}

def test_parse_with_price():
    text = "1 café de 12990, 3 jugos"
    result = parse_shopping_list_text(text)
    assert len(result) == 2
    assert result[0] == {"quantity": "1", "name": "café", "price": "12990"}
    assert result[1] == {"quantity": "3", "name": "jugos", "price": None}

# --- Price Estimation Tests ---
def test_price_estimation_with_history(client):
    # 1. Create an item
    item_res = client.post("/master/item", json={"name_standard": "Jugo de Naranja", "category_id": 1})
    item_id = item_res.json()["id"]

    # 2. Create a shopping list item and a transaction for it
    list_item_res = client.post("/list/item", json={"item_id": item_id, "planned_quantity": 1, "estimated_price": 2000})
    list_item_id = list_item_res.json()["id"]
    client.post("/transaction/add", json={"shopping_list_item_id": list_item_id, "real_quantity": 1, "real_unit_price": 2500})

    # 3. Call the estimate endpoint
    response = client.get(f"/price/estimate/{item_id}")
    assert response.status_code == 200
    assert response.json() == 2500

def test_price_estimation_no_history(client):
    # 1. Create an item without any transaction history
    item_res = client.post("/master/item", json={"name_standard": "Papas Fritas", "category_id": 2})
    item_id = item_res.json()["id"]

    # 2. Call the estimate endpoint
    response = client.get(f"/price/estimate/{item_id}")
    assert response.status_code == 404

# --- Auto-Classification Tests ---
def test_auto_classification_on_parse(client):
    # We parse a new item that should be classified as "Lácteos" by the NLP logic.
    response = client.post("/list/parse", json={"text_input": "2 yogures de 1500"})

    assert response.status_code == 200
    parsed_list = response.json()
    assert len(parsed_list) == 1

    # Check the created item's category
    item_data = parsed_list[0]["item"]
    assert item_data["name_standard"] == "yogures"
    assert item_data["category"] is not None
    assert item_data["category"]["name"] == "Lácteos"

# --- OCR and Price Comparison Tests ---
def test_ocr_price_comparison(client):
    # 1. Setup: Create items and manual transactions
    # Item 1: leche (no discrepancy)
    item1_res = client.post("/master/item", json={"name_standard": "leche", "category_id": 1})
    li1_res = client.post("/list/item", json={"item_id": item1_res.json()["id"], "planned_quantity": 1})
    client.post("/transaction/add", json={"shopping_list_item_id": li1_res.json()["id"], "real_quantity": 1, "real_unit_price": 1000.0})

    # Item 2: café (with discrepancy > 5%)
    item2_res = client.post("/master/item", json={"name_standard": "café", "category_id": 1})
    li2_res = client.post("/list/item", json={"item_id": item2_res.json()["id"], "planned_quantity": 1})
    client.post("/transaction/add", json={"shopping_list_item_id": li2_res.json()["id"], "real_quantity": 1, "real_unit_price": 12000.0})

    # Item 3: tortillas (no discrepancy)
    item3_res = client.post("/master/item", json={"name_standard": "tortillas", "category_id": 1})
    li3_res = client.post("/list/item", json={"item_id": item3_res.json()["id"], "planned_quantity": 1})
    client.post("/transaction/add", json={"shopping_list_item_id": li3_res.json()["id"], "real_quantity": 1, "real_unit_price": 4000.0})

    # 2. Call the OCR endpoint
    # We pass a dummy shopping_list_id (e.g., 1) and a dummy file.
    dummy_file_content = b"dummy invoice content"
    response = client.post(
        "/invoice/ocr?shopping_list_id=1",
        files={"invoice_image": ("invoice.jpg", dummy_file_content, "image/jpeg")}
    )

    # 3. Assert the results
    assert response.status_code == 200
    result = response.json()

    assert "discrepancies" in result
    assert len(result["discrepancies"]) == 1

    discrepancy = result["discrepancies"][0]
    assert discrepancy["item_name_manual"] == "café"
    assert discrepancy["price_manual"] == 12000.0
    assert discrepancy["item_name_ocr"] == "café"
    assert discrepancy["price_ocr"] == 13500.0
    assert "discrepancy_percentage" in discrepancy