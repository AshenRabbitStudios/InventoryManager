import unittest
import os
from decimal import Decimal
from datetime import datetime, timedelta

# Set environment variable before importing models
os.environ['INVENTORYMANAGER_ENV'] = 'test'

from models import db, Filament, Product, Sale, Part
from database import reset_database
from services.inventory_service import InventoryService

class TestInventoryService(unittest.TestCase):
    def setUp(self):
        reset_database()
        db.connect(reuse_if_open=True)

    def tearDown(self):
        db.close()

    def test_filament_crud(self):
        # Create
        fil = InventoryService.save_filament(
            brand="BrandA", material="PLA", color="Red",
            cost_per_roll=Decimal('15.00'), grams_per_roll=Decimal('1000'),
            grams_remaining=Decimal('1000'), rolls_in_stock=2
        )
        self.assertIsNotNone(fil.id)
        
        # Read
        all_fils = list(InventoryService.get_all_filaments())
        self.assertEqual(len(all_fils), 1)
        self.assertEqual(all_fils[0].color, "Red")
        
        # Update
        InventoryService.save_filament(fil.id, color="Blue")
        fil_updated = Filament.get_by_id(fil.id)
        self.assertEqual(fil_updated.color, "Blue")
        
        # Delete
        InventoryService.delete_filament(fil.id)
        self.assertEqual(len(list(InventoryService.get_all_filaments())), 0)

    def test_product_crud_with_parts(self):
        fil = Filament.create(brand="G", material="PLA", color="White", cost_per_roll=10, grams_per_roll=1000)
        
        product_data = {
            'product_type': 'TestProd',
            'size': 'L',
            'color_variant': 'White',
            'inventory_count': 5
        }
        
        # Use deep copy-like structure to avoid pop() issues in repeated calls
        parts_data = [
            {
                'name': 'Body',
                'print_time_hours': 2.5,
                'filament_usage': {fil: 50.0}
            }
        ]
        
        # Create
        prod = InventoryService.save_product(product_data=product_data, parts_data=[d.copy() for d in parts_data])
        self.assertIsNotNone(prod.id)
        self.assertEqual(prod.parts.count(), 1)
        self.assertEqual(prod.total_filament_usage[fil], Decimal('50.0'))
        
        # Update - Add another part and change inventory
        product_data['inventory_count'] = 10
        parts_data.append({
            'name': 'Lid',
            'print_time_hours': 1.0,
            'filament_usage': {fil: 20.0}
        })
        
        InventoryService.save_product(product_id=prod.id, product_data=product_data, parts_data=[d.copy() for d in parts_data])
        
        prod_updated = Product.get_by_id(prod.id)
        self.assertEqual(prod_updated.inventory_count, 10)
        self.assertEqual(prod_updated.parts.count(), 2)
        self.assertEqual(prod_updated.total_filament_usage[fil], Decimal('70.0'))
        
        # Delete
        InventoryService.delete_product(prod.id)
        self.assertEqual(Product.select().count(), 0)
        self.assertEqual(Part.select().count(), 0) # Should be deleted via CASCADE

    def test_sale_update_and_reversion(self):
        fil = Filament.create(brand="G", material="PLA", color="White", cost_per_roll=10, 
                               grams_per_roll=1000, grams_remaining=1000, rolls_in_stock=0)
        prod = Product.create(product_type='TestProd', size='L', color_variant='White', inventory_count=10)
        prod.add_filament_usage(fil, 100)
        
        # Record sale
        sales = InventoryService.create_sale(prod, 1, 20.00)
        sale = sales[0]
        
        # Check inventory after sale
        prod = Product.get_by_id(prod.id)
        fil = Filament.get_by_id(fil.id)
        self.assertEqual(prod.inventory_count, 9)
        self.assertEqual(fil.grams_remaining, 900)
        
        # Update sale (change value)
        InventoryService.update_sale(sale.id, total_value=Decimal('25.00'))
        sale = Sale.get_by_id(sale.id)
        self.assertEqual(sale.total_value, Decimal('25.00'))
        
        # Delete sale (should revert inventory)
        InventoryService.delete_sale(sale.id)
        prod = Product.get_by_id(prod.id)
        fil = Filament.get_by_id(fil.id)
        self.assertEqual(prod.inventory_count, 10)
        # Total filament: 1000g. 
        # Since adjust_inventory(-100) on 900g remaining results in 1000g,
        # which is shifted to 1 roll and 0g remaining.
        self.assertEqual(fil.grams_remaining + (fil.rolls_in_stock * fil.grams_per_roll), 1000)

    def test_analytics_data(self):
        prod = Product.create(product_type='TestProd', size='L', color_variant='White', print_time_hours=1.0)
        fil = Filament.create(brand="G", material="PLA", color="White", cost_per_roll=10, grams_per_roll=1000)
        prod.add_filament_usage(fil, 100) # Cost: 1.00
        
        now = datetime.now()
        Sale.create(product=prod, total_value=Decimal('20.00'), date=now)
        Sale.create(product=prod, total_value=Decimal('25.00'), date=now - timedelta(days=1))
        
        data = InventoryService.get_analytics_data(now - timedelta(days=2), now + timedelta(days=1))
        
        self.assertEqual(data['total_sales_count'], 2)
        self.assertEqual(data['gross_revenue'], Decimal('45.00'))
        self.assertEqual(data['total_cost'], Decimal('2.00')) # 1.00 * 2
        self.assertEqual(data['net_profit'], Decimal('43.00'))
        self.assertTrue(str(prod) in data['product_breakdown'])
        self.assertEqual(data['product_breakdown'][str(prod)]['count'], 2)
        self.assertEqual(len(data['daily_stats']), 2)

    def test_todo_data(self):
        # Setup filaments
        fil = Filament.create(brand="G", material="PLA", color="White", cost_per_roll=10, 
                               grams_per_roll=1000, grams_remaining=100, rolls_in_stock=0)
        
        # Setup product that needs stock (inventory < 3)
        prod = Product.create(product_type='NeedStock', size='L', color_variant='White', inventory_count=1)
        prod.add_filament_usage(fil, 100)
        
        # Add some sales to make it priority
        for _ in range(5):
            Sale.create(product=prod, total_value=Decimal('10.00'))
            
        todo = InventoryService.get_todo_data()
        
        # Should be in to_print
        self.assertTrue(any(p.id == prod.id for p in todo['to_print']))
        
        # Should have filament to order (since 100g < buffer/todo needs)
        self.assertTrue(len(todo['to_order']) > 0)
        self.assertTrue(any(item['filament'].id == fil.id for item in todo['to_order']))

if __name__ == '__main__':
    unittest.main()
