import re
from typing import List, Dict, Optional

def parse_shopping_list_text(text: str) -> List[Dict[str, Optional[str]]]:
    """
    Parses a conversational shopping list string into a structured list of items.

    Example input: "2 leches, 1 café de 12990, y 6 tortillas"
    Example output:
    [
        {'quantity': '2', 'name': 'leches', 'price': None},
        {'quantity': '1', 'name': 'café', 'price': '12990'},
        {'quantity': '6', 'name': 'tortillas', 'price': None}
    ]
    """
    # Regex to capture: quantity, name, and an optional price preceded by "de"
    # It handles integers and basic decimals for quantity.
    item_pattern = re.compile(
        r"(\d+\.?\d*)\s+([\w\s]+?)(?:\s+de\s+\$?(\d+))?$"
    )

    # Split the text by commas or "y"
    # This is a simple way to separate items in the list.
    items_str = re.split(r'\s*,\s*|\s+y\s+', text.strip())

    parsed_items = []
    for item_text in items_str:
        if not item_text:
            continue

        match = item_pattern.match(item_text.strip())
        if match:
            quantity, name, price = match.groups()
            parsed_items.append({
                "quantity": quantity,
                "name": name.strip(),
                "price": price
            })

    return parsed_items

def classify_item_category(db, item_name: str) -> Optional[int]:
    """
    Tries to classify an item into a category based on keywords in its name.

    This is a simple rule-based classifier. A more advanced version could use
    machine learning models.

    Returns the category ID if a match is found, otherwise None.
    """
    # In a real app, this mapping could be stored in the DB or a config file.
    keyword_to_category = {
        "leche": "Lácteos",
        "yogur": "Lácteos",
        "queso": "Lácteos",
        "pan": "Panadería",
        "tortilla": "Panadería",
        "café": "Bebidas",
        "jugo": "Bebidas",
        "carne": "Carnes",
        "pollo": "Carnes",
        "fruta": "Frutas y Verduras",
        "verdura": "Frutas y Verduras",
    }

    from . import crud # Local import to avoid circular dependency issues

    # Normalize the item name to lower case for matching
    lower_item_name = item_name.lower()

    for keyword, category_name in keyword_to_category.items():
        if keyword in lower_item_name:
            # We found a keyword, now get the category ID from the DB
            category = crud.get_category_by_name(db, name=category_name)
            if category:
                return category.id

    return None