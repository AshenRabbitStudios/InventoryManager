import unittest
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Set environment variable before importing models
os.environ['INVENTORYMANAGER_ENV'] = 'test'

from models import db, Filament, Product, Sale
from database import reset_database
from services.prediction_service import PredictionService

class TestPredictionService(unittest.TestCase):
    def setUp(self):
        reset_database()
        db.connect(reuse_if_open=True)
        
        # Setup basic data
        self.filament = Filament.create(
            brand="Generic", material="PLA", color="Black",
            cost_per_roll=Decimal('15.00'), grams_per_roll=Decimal('1000')
        )
        self.product = Product.create(
            product_type="Gothic hide", size="XL", color_variant="Black",
            inventory_count=5
        )

    def tearDown(self):
        db.close()

    def test_predict_sales_next_30_days_no_sales(self):
        prediction = PredictionService.predict_sales_next_30_days(self.product.id)
        self.assertEqual(prediction, 0.0)

    def test_predict_sales_next_30_days_with_sales(self):
        # Create 9 sales in the last 90 days
        # Simple average: 9 / 3 = 3.0 predicted for next 30 days
        now = datetime.now()
        for i in range(9):
            Sale.create(
                product=self.product,
                total_value=Decimal('10.00'),
                date=now - timedelta(days=i*5) # Spread them out
            )
        
        prediction = PredictionService.predict_sales_next_30_days(self.product.id)
        self.assertEqual(prediction, 3.0)

    def test_predict_sales_next_30_days_out_of_range(self):
        # Create sales more than 90 days ago
        now = datetime.now()
        Sale.create(
            product=self.product,
            total_value=Decimal('10.00'),
            date=now - timedelta(days=95)
        )
        
        prediction = PredictionService.predict_sales_next_30_days(self.product.id)
        self.assertEqual(prediction, 0.0)

    def test_get_low_stock_alerts(self):
        # product has inventory_count=5
        
        # Threshold 2: should be empty
        alerts = PredictionService.get_low_stock_alerts(threshold=2)
        self.assertEqual(len(alerts), 0)
        
        # Threshold 5: should include our product
        alerts = PredictionService.get_low_stock_alerts(threshold=5)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].id, self.product.id)
        
        # Create another product with low stock
        p2 = Product.create(
            product_type="Widget", size="S", color_variant="Red",
            inventory_count=1
        )
        
        alerts = PredictionService.get_low_stock_alerts(threshold=2)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].id, p2.id)

if __name__ == '__main__':
    unittest.main()
