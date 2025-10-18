from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from pydantic import BaseModel

from .. import crud
from ..database import get_db
from ..models.models import ShoppingListItem, TransactionDetail, ItemMaster, CategoryMaster

router = APIRouter()

# --- Response Schemas for Reports ---
class SpendingComparison(BaseModel):
    total_estimated: float
    total_real: float
    variation_percentage: float

class SpendingByCategory(BaseModel):
    category: str
    total_spent: float

class PriceDiscrepancy(BaseModel):
    item_name: str
    estimated_price: float
    real_price: float
    difference: float

class PriceTrend(BaseModel):
    purchase_date: str
    price: float

# --- Reporting Endpoints ---

@router.get("/report/spending-comparison", response_model=SpendingComparison)
def get_spending_comparison(db: Session = Depends(get_db)):
    """
    Compares the total estimated spending with the total real spending.
    """
    shopping_list_items = db.query(ShoppingListItem).all()

    total_estimated = sum(item.estimated_price * item.planned_quantity for item in shopping_list_items if item.estimated_price)

    transactions = db.query(TransactionDetail).all()
    total_real = sum(t.real_unit_price * t.real_quantity for t in transactions)

    variation = 0
    if total_estimated > 0:
        variation = ((total_real - total_estimated) / total_estimated) * 100

    return {
        "total_estimated": total_estimated,
        "total_real": total_real,
        "variation_percentage": variation
    }

@router.get("/report/spending-by-category", response_model=List[SpendingByCategory])
def get_spending_by_category(db: Session = Depends(get_db)):
    """
    Calculates the total spending for each category.
    """
    category_spending = db.query(
        CategoryMaster.name,
        func.sum(TransactionDetail.real_unit_price * TransactionDetail.real_quantity)
    ).join(ItemMaster, CategoryMaster.id == ItemMaster.category_id)\
     .join(ShoppingListItem, ItemMaster.id == ShoppingListItem.item_id)\
     .join(TransactionDetail, ShoppingListItem.id == TransactionDetail.shopping_list_item_id)\
     .group_by(CategoryMaster.name)\
     .all()

    return [{"category": name, "total_spent": total} for name, total in category_spending]

@router.get("/report/discrepancy-analysis", response_model=List[PriceDiscrepancy])
def get_discrepancy_analysis(db: Session = Depends(get_db)):
    """
    Lists products where the estimated price differed significantly from the real price.
    """
    discrepancies = []
    transactions = db.query(TransactionDetail).all()
    for t in transactions:
        estimated = t.shopping_list_item.estimated_price
        real = t.real_unit_price
        if estimated and real: # Ensure both prices are available
            difference = real - estimated
            # Example threshold: consider any difference significant for now
            if abs(difference) > 0.01:
                discrepancies.append({
                    "item_name": t.shopping_list_item.item.name_standard,
                    "estimated_price": estimated,
                    "real_price": real,
                    "difference": difference
                })
    return discrepancies

@router.get("/report/price-trends/{item_id}", response_model=List[PriceTrend])
def get_price_trends(item_id: int, db: Session = Depends(get_db)):
    """
    Shows the historical price evolution for a selected product.
    """
    transactions = crud.get_transactions_by_item(db, item_id=item_id)

    if not transactions:
        return []

    return [
        {
            "purchase_date": t.purchase_date.strftime("%Y-%m-%d"),
            "price": t.real_unit_price
        }
        for t in sorted(transactions, key=lambda x: x.purchase_date)
    ]