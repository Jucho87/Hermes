from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import crud
from ..schemas.schemas import ShoppingListItem, ShoppingListItemCreate, ShoppingListItemUpdate, ItemMasterCreate, TextInput
from ..database import get_db
from .. import nlp

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

@router.post("/list/parse", response_model=List[ShoppingListItem])
def parse_list(text_input: TextInput, db: Session = Depends(get_db)):
    """
    Parses a conversational shopping list string and adds items to the list.
    Example: "2 leches, 1 café de 12990, y 6 tortillas"
    """
    parsed_items_nlp = nlp.parse_shopping_list_text(text_input.text_input)
    if not parsed_items_nlp:
        raise HTTPException(status_code=400, detail="Could not parse any items from the input text.")

    created_list_items = []
    for parsed_item in parsed_items_nlp:
        item_name = parsed_item["name"]

        # 1. Find or create the master item
        db_item = crud.get_item_by_name(db, name=item_name)
        if not db_item:
            # If item doesn't exist, create it.
            item_master_create = ItemMasterCreate(name_standard=item_name)
            db_item = crud.create_item(db, item=item_master_create)

            # Now, try to classify the new item automatically
            category_id = nlp.classify_item_category(db, item_name=item_name)
            if category_id:
                db_item.category_id = category_id
                db.commit()
                db.refresh(db_item)

        # 2. Create the shopping list item
        shopping_list_create = ShoppingListItemCreate(
            item_id=db_item.id,
            planned_quantity=float(parsed_item["quantity"]),
            estimated_price=float(parsed_item["price"]) if parsed_item["price"] else None
        )
        created_item = crud.create_shopping_list_item(db, item=shopping_list_create)
        created_list_items.append(created_item)

    return created_list_items

@router.get("/price/estimate/{item_id}", response_model=float)
def estimate_price(item_id: int, db: Session = Depends(get_db)):
    """
    Estimates the price of an item based on its most recent purchase price.
    """
    # 1. Check if item exists
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found in master")

    # 2. Get the last known price
    last_price = crud.get_last_price_for_item(db, item_id=item_id)
    if last_price is None:
        # If no historical price, we can't provide an estimate.
        raise HTTPException(status_code=404, detail="No historical price found for this item to make an estimation.")

    return last_price