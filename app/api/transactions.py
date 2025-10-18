from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import crud
from ..schemas.schemas import TransactionDetail, TransactionDetailCreate
from ..database import get_db

router = APIRouter()

@router.post("/transaction/add", response_model=TransactionDetail)
def add_transaction(transaction: TransactionDetailCreate, db: Session = Depends(get_db)):
    # Check if the shopping list item exists
    shopping_item = crud.get_shopping_list_item(db, item_id=transaction.shopping_list_item_id)

    if not shopping_item:
        raise HTTPException(status_code=404, detail="Shopping list item not found")

    if shopping_item.status == 'purchased':
        raise HTTPException(status_code=400, detail="This item has already been marked as purchased")

    return crud.create_transaction(db=db, transaction=transaction)