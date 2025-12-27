import unittest
import os
from decimal import Decimal

# Set environment variable before importing models
os.environ['INVENTORYMANAGER_ENV'] = 'test'

from models import db, Filament, Product, Part
from database import reset_database

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        # Ensure we are using the test database
        reset_database()
        db.connect(reuse_if_open=True)

    def tearDown(self):
        db.close()

class TestGothicHide(BaseTestCase):
    def test_gothic_hide_calculations(self):
        """
        Tests the 'Gothic hide' product as described in the issue.
        """
        # Create Filaments
        black_pla = Filament.create(
            brand="Generic",
            material="PLA",
            color="Black Matte",
            cost_per_roll=Decimal('14.28'),
            grams_per_roll=Decimal('1000')
        )
        pink_pla = Filament.create(
            brand="Generic",
            material="PLA",
            color="Pink Matte",
            cost_per_roll=Decimal('15.00'),
            grams_per_roll=Decimal('1000')
        )

        # Create Product
        product = Product.create(
            product_type="Gothic hide",
            size="XL",
            color_variant="Black/Pink"
        )

        # Add Parts
        # Lid: 161.67g black, 29.51g pink, 9h37m (9.616... hours)
        lid = product.add_part("Lid", print_time_hours=9.617) # 9h 37m is approx 9.617h
        lid.add_filament_usage(black_pla, 161.67)
        lid.add_filament_usage(pink_pla, 29.51)

        # Base: 368.88g black, 37.57g pink, 11h
        base = product.add_part("Base", print_time_hours=11.0)
        base.add_filament_usage(black_pla, 368.88)
        base.add_filament_usage(pink_pla, 37.57)

        # Skull: 33.9g pink, 1h 35m (1.583... hours)
        skull = product.add_part("Skull", print_time_hours=1.583) # 1h 35m is approx 1.583h
        skull.add_filament_usage(pink_pla, 33.9)

        # Assertions
        
        # Total Print Time: 9.617 + 11.0 + 1.583 = 22.2
        self.assertEqual(product.total_print_time, Decimal('22.20'))

        # Total Filament Usage
        usage = product.total_filament_usage
        self.assertEqual(usage[black_pla], Decimal('530.55'))
        self.assertEqual(usage[pink_pla], Decimal('100.98'))

        # Total Cost
        # Black: (530.55 / 1000) * 14.28 = 7.576254
        # Pink: (100.98 / 1000) * 15.00 = 1.5147
        # Total: 7.576254 + 1.5147 = 9.090954 -> 9.09
        self.assertEqual(product.total_cost, Decimal('9.09'))

if __name__ == '__main__':
    unittest.main()
