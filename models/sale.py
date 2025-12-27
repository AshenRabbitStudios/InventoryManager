from peewee import ForeignKeyField, DateTimeField, IntegerField, DecimalField
from datetime import datetime
from .base import BaseModel
from .product import Product

class Sale(BaseModel):
    """
    Represents a sale event. Each record represents a single unit.
    """
    date = DateTimeField(default=datetime.now)
    product = ForeignKeyField(Product, backref='sales', on_delete='CASCADE')
    total_value = DecimalField(decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d %H:%M')} - {self.product} for ${self.total_value}"