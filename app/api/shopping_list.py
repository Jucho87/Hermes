from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import crud
from ..schemas.schemas import ShoppingListItem, ShoppingListItemCreate, ShoppingListItemUpdate, ItemMasterCreate
from ..database import get_db

router = APIRouter()

@router.post("/list/item", response_model=ShoppingListItem)
def create_shopping_list_item(item: ShoppingListItemCreate, db: Session = Depends(get_db)):
    # Check if item exists in master
    db_item = crud.get_item(db, item_id=item.item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Master item not found")
    return crud.create_shopping_list_item(db=db, item=item)

@router.get("/list/items", response_model=List[ShoppingListItem])
def read_shopping_list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_shopping_list_items(db, skip=skip, limit=limit)
    return items

@router.patch("/list/update/{item_id}", response_model=ShoppingListItem)
def update_shopping_list_item(item_id: int, item: ShoppingListItemUpdate, db: Session = Depends(get_db)):
    db_item = crud.update_shopping_list_item(db, item_id=item_id, item=item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Shopping list item not found")
    return db_item

@router.delete("/list/item/{item_id}", response_model=ShoppingListItem)
def delete_shopping_list_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.delete_shopping_list_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Shopping list item not found")
    return db_item

# Placeholder for conversational input
class ParsedItem(ItemMasterCreate):
    planned_quantity: float
    estimated_price: Optional[float] = None

@router.post("/list/parse", response_model=List[ShoppingListItem])
def parse_list(text_input: str, db: Session = Depends(get_db)):
    """
    ## Simple Parser (Temporary)
    This is a temporary endpoint that simulates the parsing of conversational input.
    **It does not use AI yet.**

    **Expected format:** A list of items separated by semicolons (;).
    Each item must be in the format: `name,category_id,quantity,price`
    Example: `Leche,1,2,1.50;Pan,2,1,0.50`
    """
    parsed_items = []
    items = text_input.strip().split(';')
    for item_str in items:
        try:
            name, category_id, quantity, price = item_str.split(',')

            # 1. Find or create master item
            db_item = crud.get_item_by_name(db, name=name)
            if not db_item:
                 # Check if category exists
                db_category = crud.get_category(db, category_id=int(category_id))
                if not db_category:
                    raise HTTPException(status_code=400, detail=f"Category with ID {category_id} not found for new item '{name}'")
                item_master_create = ItemMasterCreate(name_standard=name, category_id=int(category_id))
                db_item = crud.create_item(db, item=item_master_create)

            # 2. Create shopping list item
            shopping_list_create = ShoppingListItemCreate(
                item_id=db_item.id,
                planned_quantity=float(quantity),
                estimated_price=float(price)
            )
            created_list_item = crud.create_shopping_list_item(db, item=shopping_list_create)
            parsed_items.append(created_list_item)

        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid format for item string: '{item_str}'. Expected 'name,category_id,quantity,price'.")
    return parsed_items

# Placeholder for price estimation
@router.get("/price/estimate/{item_id}", response_model=float)
def estimate_price(item_id: int, db: Session = Depends(get_db)):
    """
    ## Price Estimator (Placeholder)
    This is a placeholder for the price estimation service.
    For now, it returns a fixed value.
    """
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    # In a real scenario, this would involve a more complex lookup
    return 10.0  # Placeholder price