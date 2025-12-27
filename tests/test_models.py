import unittest
import os
from decimal import Decimal

# Set environment variable before importing models
os.environ['INVENTORYMANAGER_ENV'] = 'test'

from models import db, Filament, Product
from database import reset_database

class TestModelLogic(unittest.TestCase):
    def setUp(self):
        reset_database()
        db.connect(reuse_if_open=True)

    def tearDown(self):
        db.close()

    def test_filament_adjust_inventory_depletion(self):
        # 1 roll in stock + 500g remaining = 1500g total
        fil = Filament.create(
            brand="Test", material="PLA", color="Red", cost_per_roll=20,
            grams_per_roll=1000, grams_remaining=500, rolls_in_stock=1
        )
        
        # Use 600g
        fil.adjust_inventory(600)
        # Should use 500g from remaining, then 100g from the next roll
        # 1 roll used -> rolls_in_stock=0
        # New roll: 1000 - 100 = 900g
        self.assertEqual(fil.rolls_in_stock, 0)
        self.assertEqual(fil.grams_remaining, 900)
        
        # Use another 1000g? No, use 800g
        fil.adjust_inventory(800)
        self.assertEqual(fil.rolls_in_stock, 0)
        self.assertEqual(fil.grams_remaining, 100)
        
        # Use 150g (depletes it)
        fil.adjust_inventory(150)
        self.assertEqual(fil.rolls_in_stock, 0)
        self.assertEqual(fil.grams_remaining, -50) # It stays negative if no rolls left? 
        # Actually, the logic is: while self.grams_remaining < 0 and self.rolls_in_stock > 0:
        # So it will stay negative if no rolls in stock.

    def test_filament_adjust_inventory_reversal(self):
        # 0 rolls in stock + 100g remaining = 100g total
        fil = Filament.create(
            brand="Test", material="PLA", color="Red", cost_per_roll=20,
            grams_per_roll=1000, grams_remaining=100, rolls_in_stock=0
        )
        
        # Add back 1000g
        fil.adjust_inventory(-1000)
        # 100 - (-1000) = 1100
        # 1100 >= 1000 -> rolls_in_stock=1, grams_remaining=100
        self.assertEqual(fil.rolls_in_stock, 1)
        self.assertEqual(fil.grams_remaining, 100)

    def test_product_adjust_inventory(self):
        p = Product.create(product_type="Test", size="L", color_variant="X", inventory_count=10)
        p.adjust_inventory(-3)
        self.assertEqual(p.inventory_count, 7)
        p.adjust_inventory(5)
        self.assertEqual(p.inventory_count, 12)

if __name__ == '__main__':
    unittest.main()
