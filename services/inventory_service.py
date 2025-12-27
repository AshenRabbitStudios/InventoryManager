from models import Sale, SaleItem, Product, db
from datetime import datetime

class InventoryService:
    """
    Service layer to handle business logic and manage the state between the 
    GUI and the Database.
    """

    @staticmethod
    def create_sale(items_data):
        """
        Creates a complete sale with multiple items in a single transaction.
        
        items_data: List of dicts [{'product': product_obj, 'quantity': int}, ...]
        """
        with db.atomic():
            new_sale = Sale.create()
            for item in items_data:
                SaleItem.create(
                    sale=new_sale,
                    product=item['product'],
                    quantity=item['quantity']
                )
            return new_sale

    @staticmethod
    def get_active_sales():
        """
        Returns all sales with their items and products pre-loaded 
        to avoid N+1 query issues. This makes 'sale.items' access 
        instant without further DB calls.
        """
        from models import SaleItem
        sales = Sale.select().order_by(Sale.date.desc())
        return sales.prefetch(SaleItem, Product)

class SaleDraft:
    """
    A helper class for the GUI to manage a sale in memory before 
    committing it to the database.
    """
    def __init__(self):
        self.items = []  # List of (product, quantity)

    def add_item(self, product, quantity):
        self.items.append({'product': product, 'quantity': quantity})

    def remove_item(self, index):
        if 0 <= index < len(self.items):
            self.items.pop(index)

    def save(self):
        """Commits the draft to the database using the service."""
        if not self.items:
            return None
        return InventoryService.create_sale(self.items)
