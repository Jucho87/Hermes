import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from ..database import Base

class CategoryMaster(Base):
    __tablename__ = "category_master"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    items = relationship("ItemMaster", back_populates="category")

class ItemMaster(Base):
    __tablename__ = "item_master"

    id = Column(Integer, primary_key=True, index=True)
    name_standard = Column(String, unique=True, index=True, nullable=False)
    category_id = Column(Integer, ForeignKey("category_master.id"))

    category = relationship("CategoryMaster", back_populates="items")
    shopping_list_entries = relationship("ShoppingListItem", back_populates="item")

class ShoppingListItem(Base):
    __tablename__ = "shopping_list_item"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("item_master.id"))
    planned_quantity = Column(Float, nullable=False)
    estimated_price = Column(Float)
    status = Column(String, default='planned', nullable=False) # planned, purchased

    item = relationship("ItemMaster", back_populates="shopping_list_entries")
    transaction = relationship("TransactionDetail", back_populates="shopping_list_item", uselist=False)


class TransactionDetail(Base):
    __tablename__ = "transaction_detail"

    id = Column(Integer, primary_key=True, index=True)
    shopping_list_item_id = Column(Integer, ForeignKey("shopping_list_item.id"))
    real_quantity = Column(Float, nullable=False)
    real_unit_price = Column(Float, nullable=False)
    purchase_date = Column(DateTime, default=datetime.datetime.utcnow)

    shopping_list_item = relationship("ShoppingListItem", back_populates="transaction")