import unittest
import os
from decimal import Decimal

# Set environment variable before importing models
os.environ['INVENTORYMANAGER_ENV'] = 'test'

from models import db, Filament, Product, Part, Sale
from database import reset_database
from services.inventory_service import InventoryService

class TestOverviewLogic(unittest.TestCase):
    def setUp(self):
        reset_database()
        db.connect(reuse_if_open=True)

    def tearDown(self):
        db.close()

    def test_printable_count(self):
        # Create Filament: 1000g roll + 1 roll in stock = 2000g total
        f = Filament.create(
            brand="Test", material="PLA", color="Red",
            cost_per_roll=Decimal('20.00'), grams_per_roll=Decimal('1000'),
            grams_remaining=Decimal('1000'), rolls_in_stock=1
        )
        
        # Product uses 100g
        p = Product.create(product_type="Widget", size="M", color_variant="Red")
        p.add_filament_usage(f, 100)
        
        # Should be able to print 20
        count = InventoryService.calculate_printable_count(p)
        self.assertEqual(count, 20)
        
        # Change usage to 300g
        pf = p.filament_usage[0]
        pf.grams_needed = Decimal('300')
        pf.save()
        
        # 2000 / 300 = 6.66 -> 6
        count = InventoryService.calculate_printable_count(p)
        self.assertEqual(count, 6)

    def test_sale_creation_and_inventory_decrement(self):
        p = Product.create(product_type="Widget", size="M", color_variant="Red", inventory_count=10)
        
        # Test creating a sale for 3 widgets, total $45
        sales = InventoryService.create_sale(p, 3, 45.00)
        
        # Verify 3 sale records were created
        self.assertEqual(len(sales), 3)
        for s in sales:
            self.assertEqual(s.total_value, Decimal('15.00'))
            self.assertEqual(s.product, p)
        
        # Verify inventory decrement
        p_refreshed = Product.get_by_id(p.id)
        self.assertEqual(p_refreshed.inventory_count, 7)

    def test_sale_creation_precision(self):
        p = Product.create(product_type="Widget", size="M", color_variant="Red", inventory_count=10)
        
        # Test creating a sale for 3 widgets, total $10 (should split as 3.33, 3.33, 3.34)
        sales = InventoryService.create_sale(p, 3, 10.00)
        
        values = sorted([s.total_value for s in sales])
        self.assertEqual(values, [Decimal('3.33'), Decimal('3.33'), Decimal('3.34')])
        self.assertEqual(sum(values), Decimal('10.00'))

if __name__ == '__main__':
    unittest.main()
