from peewee import ForeignKeyField, DateTimeField, IntegerField
from datetime import datetime
from .base import BaseModel
from .product import Product

class Sale(BaseModel):
    """
    Represents a sale event.
    """
    date = DateTimeField(default=datetime.now)

class SaleItem(BaseModel):
    """
    Represents an individual product within a sale.
    """
    sale = ForeignKeyField(Sale, backref='items', on_delete='CASCADE')
    product = ForeignKeyField(Product, backref='sale_items', on_delete='CASCADE')
    quantity = IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product}"