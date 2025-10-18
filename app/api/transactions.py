from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from .. import crud
from ..schemas.schemas import TransactionDetail, TransactionDetailCreate, OCRResult
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

@router.post("/invoice/ocr", response_model=OCRResult)
async def upload_invoice_for_ocr(
    shopping_list_id: int,
    invoice_image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    ## Upload Invoice for OCR Processing and Price Comparison

    This endpoint simulates uploading an invoice, processing it with OCR,
    and compares the results with manually entered transaction data.

    - **shopping_list_id**: An ID of any item in the shopping session to verify.
    - **invoice_image**: The uploaded invoice image file.
    """
    # --- OCR Simulation ---
    simulated_ocr_data = [
        {"item_name": "leche", "price": 1050.0},
        {"item_name": "café", "price": 13500.0}, # Deliberate difference for testing
        {"item_name": "tortillas", "price": 4000.0},
    ]

    # --- Price Comparison Logic ---
    manual_transactions = crud.get_transactions_by_shopping_list_item_id(db, shopping_list_id)

    discrepancies = []

    for ocr_item in simulated_ocr_data:
        ocr_name = ocr_item["item_name"].lower()
        ocr_price = ocr_item["price"]

        # Find a matching manual transaction
        for manual_t in manual_transactions:
            manual_name = manual_t.shopping_list_item.item.name_standard.lower()

            if ocr_name in manual_name or manual_name in ocr_name:
                manual_price = manual_t.real_unit_price

                # Check for price discrepancy (e.g., > 5%)
                if abs(manual_price - ocr_price) / manual_price > 0.05:
                    discrepancy = {
                        "item_name_manual": manual_name,
                        "price_manual": manual_price,
                        "item_name_ocr": ocr_name,
                        "price_ocr": ocr_price,
                        "discrepancy_percentage": ((ocr_price - manual_price) / manual_price) * 100
                    }
                    discrepancies.append(discrepancy)
                break # Move to the next OCR item once a match is found

    return {
        "discrepancies": discrepancies,
        "message": "Comparison complete. Found {} discrepancies.".format(len(discrepancies))
    }