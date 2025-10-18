from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import crud
from ..schemas.schemas import Category, CategoryCreate, ItemMaster, ItemMasterCreate
from ..database import get_db

router = APIRouter()

# --- Category Endpoints ---

@router.post("/master/category", response_model=Category)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = crud.get_category_by_name(db, name=category.name)
    if db_category:
        raise HTTPException(status_code=400, detail="Category already registered")
    return crud.create_category(db=db, category=category)


@router.get("/master/categories", response_model=List[Category])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = crud.get_categories(db, skip=skip, limit=limit)
    return categories


@router.get("/master/category/{category_id}", response_model=Category)
def read_category(category_id: int, db: Session = Depends(get_db)):
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

# --- Item Master Endpoints ---

@router.post("/master/item", response_model=ItemMaster)
def create_item(item: ItemMasterCreate, db: Session = Depends(get_db)):
    return crud.create_item(db=db, item=item)


@router.get("/master/items", response_model=List[ItemMaster])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


@router.get("/master/item/{item_id}", response_model=ItemMaster)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item