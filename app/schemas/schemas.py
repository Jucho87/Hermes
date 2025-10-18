from pydantic import BaseModel
from typing import Optional, List
import datetime

# --- Category Schemas ---
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True

# --- General Schemas ---
class TextInput(BaseModel):
    text_input: str

# --- Item Master Schemas ---
class ItemMasterBase(BaseModel):
    name_standard: str
    category_id: Optional[int] = None

class ItemMasterCreate(ItemMasterBase):
    pass

class ItemMaster(ItemMasterBase):
    id: int
    category: Category

    class Config:
        from_attributes = True

# --- Shopping List Item Schemas ---
class ShoppingListItemBase(BaseModel):
    item_id: int
    planned_quantity: float
    estimated_price: Optional[float] = None

class ShoppingListItemCreate(ShoppingListItemBase):
    pass

class ShoppingListItemUpdate(BaseModel):
    planned_quantity: Optional[float] = None
    estimated_price: Optional[float] = None
    status: Optional[str] = None

class ShoppingListItem(ShoppingListItemBase):
    id: int
    status: str
    item: ItemMaster

    class Config:
        from_attributes = True

# --- Transaction Detail Schemas ---
class TransactionDetailBase(BaseModel):
    shopping_list_item_id: int
    real_quantity: float
    real_unit_price: float

class TransactionDetailCreate(TransactionDetailBase):
    pass

class TransactionDetail(TransactionDetailBase):
    id: int
    purchase_date: datetime.datetime

    class Config:
        from_attributes = True