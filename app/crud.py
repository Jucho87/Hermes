from sqlalchemy.orm import Session
from .models import models
from .schemas.schemas import CategoryCreate, ItemMasterCreate, ShoppingListItemCreate, ShoppingListItemUpdate, TransactionDetailCreate

# --- Category CRUD ---

def get_category(db: Session, category_id: int):
    return db.query(models.CategoryMaster).filter(models.CategoryMaster.id == category_id).first()

def get_category_by_name(db: Session, name: str):
    return db.query(models.CategoryMaster).filter(models.CategoryMaster.name == name).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.CategoryMaster).offset(skip).limit(limit).all()

def create_category(db: Session, category: CategoryCreate):
    db_category = models.CategoryMaster(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# --- Item Master CRUD ---

def get_item(db: Session, item_id: int):
    return db.query(models.ItemMaster).filter(models.ItemMaster.id == item_id).first()

def get_item_by_name(db: Session, name: str):
    return db.query(models.ItemMaster).filter(models.ItemMaster.name_standard == name).first()

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ItemMaster).offset(skip).limit(limit).all()

def create_item(db: Session, item: ItemMasterCreate):
    db_item = models.ItemMaster(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# --- Shopping List CRUD ---

def create_shopping_list_item(db: Session, item: ShoppingListItemCreate):
    db_item = models.ShoppingListItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_shopping_list_item(db: Session, item_id: int):
    return db.query(models.ShoppingListItem).filter(models.ShoppingListItem.id == item_id).first()

def get_shopping_list_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ShoppingListItem).offset(skip).limit(limit).all()

def update_shopping_list_item(db: Session, item_id: int, item: ShoppingListItemUpdate):
    db_item = db.query(models.ShoppingListItem).filter(models.ShoppingListItem.id == item_id).first()
    if db_item:
        update_data = item.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
    return db_item

def delete_shopping_list_item(db: Session, item_id: int):
    db_item = db.query(models.ShoppingListItem).filter(models.ShoppingListItem.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item

# --- Transaction Detail CRUD ---

def create_transaction(db: Session, transaction: TransactionDetailCreate):
    # 1. Create the transaction detail
    db_transaction = models.TransactionDetail(**transaction.model_dump())
    db.add(db_transaction)

    # 2. Update the status of the corresponding shopping list item
    db_shopping_item = db.query(models.ShoppingListItem).filter(models.ShoppingListItem.id == transaction.shopping_list_item_id).first()
    if db_shopping_item:
        db_shopping_item.status = 'purchased'

    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TransactionDetail).offset(skip).limit(limit).all()

def get_transactions_by_item(db: Session, item_id: int):
    return db.query(models.TransactionDetail)\
             .join(models.ShoppingListItem)\
             .filter(models.ShoppingListItem.item_id == item_id)\
             .all()

def get_last_price_for_item(db: Session, item_id: int):
    last_transaction = db.query(models.TransactionDetail)\
                         .join(models.ShoppingListItem)\
                         .filter(models.ShoppingListItem.item_id == item_id)\
                         .order_by(models.TransactionDetail.purchase_date.desc())\
                         .first()
    if last_transaction:
        return last_transaction.real_unit_price
    return None

def get_transactions_by_shopping_list_item_id(db: Session, shopping_list_item_id: int):
    """
    Simulates getting all transactions related to a single shopping trip/session.
    For now, it just returns all transactions for simplicity.
    A real implementation would need a way to group shopping list items into a session.
    """
    return db.query(models.TransactionDetail).all()