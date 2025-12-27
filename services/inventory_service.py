from models import Sale, Product, Part, Filament, ProductFilament, PartFilament, db
from datetime import datetime
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class InventoryService:
    """
    Service layer to handle business logic and manage the state between the 
    GUI and the Database.
    """

    @staticmethod
    def get_all_filaments():
        """Returns all filaments ordered by brand and color."""
        try:
            return Filament.select().order_by(Filament.brand, Filament.color)
        except Exception as e:
            logger.error(f"Error fetching filaments: {e}")
            return []

    @staticmethod
    def save_filament(filament_id=None, **data):
        """
        Creates or updates a filament.
        data: dict with brand, material, color, cost_per_roll, grams_per_roll, grams_remaining, rolls_in_stock
        """
        try:
            if filament_id:
                filament = Filament.get_by_id(filament_id)
                for key, value in data.items():
                    setattr(filament, key, value)
                filament.save()
                logger.info(f"Updated filament ID: {filament_id}")
                return filament
            else:
                filament = Filament.create(**data)
                logger.info(f"Created new filament ID: {filament.id}")
                return filament
        except Exception as e:
            logger.error(f"Error saving filament: {e}")
            raise

    @staticmethod
    def delete_filament(filament_id):
        """Deletes a filament by ID."""
        try:
            if filament_id:
                Filament.delete_by_id(filament_id)
                logger.info(f"Deleted filament ID: {filament_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting filament {filament_id}: {e}")
            raise

    @staticmethod
    def get_all_products():
        """Returns all products ordered by type, color, and size."""
        try:
            return Product.select().order_by(Product.product_type, Product.color_variant, Product.size)
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            return []

    @staticmethod
    def save_product(product_id=None, product_data=None, parts_data=None):
        """
        Creates or updates a product and its associated parts.
        product_data: dict with product_type, size, color_variant, print_time_hours, inventory_count
        parts_data: list of dicts [{'id': optional, 'name': str, 'print_time_hours': float, 'filament_usage': {filament_obj: grams}}]
        """
        try:
            with db.atomic():
                if product_id:
                    product = Product.get_by_id(product_id)
                    for key, value in product_data.items():
                        setattr(product, key, value)
                    product.save()
                else:
                    product = Product.create(**product_data)

                # Handle Parts
                if parts_data is not None:
                    # Keep track of current part IDs to delete removed ones
                    existing_part_ids = [p.id for p in product.parts]
                    updated_part_ids = []

                    for p_data in parts_data:
                        part_id = p_data.get('id')
                        filament_usage = p_data.pop('filament_usage', {})
                        
                        if part_id:
                            part = Part.get_by_id(part_id)
                            for key, value in p_data.items():
                                if key != 'id':
                                    setattr(part, key, value)
                            part.save()
                            updated_part_ids.append(part.id)
                        else:
                            part = Part.create(product=product, **p_data)
                            updated_part_ids.append(part.id)

                        # Update Filament Usage for Part
                        # Clear existing and re-add for simplicity in this junction table update
                        PartFilament.delete().where(PartFilament.part == part).execute()
                        for filament, grams in filament_usage.items():
                            if grams > 0:
                                part.add_filament_usage(filament, grams)

                    # Delete parts that were not in the update
                    for pid in existing_part_ids:
                        if pid not in updated_part_ids:
                            Part.delete_by_id(pid)

                return product
        except Exception as e:
            logger.error(f"Error saving product: {e}")
            raise

    @staticmethod
    def delete_product(product_id):
        """Deletes a product by ID."""
        try:
            if product_id:
                Product.delete_by_id(product_id)
                logger.info(f"Deleted product ID: {product_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {e}")
            raise

    @staticmethod
    def create_sale(product, quantity, total_value):
        """
        Creates a complete sale. If quantity > 1, it splits the sale into multiple records
        as per the "1 item per sale" requirement, dividing the total value equally.
        
        product: product object
        quantity: int
        total_value: float/Decimal total value for the entire quantity
        """
        try:
            with db.atomic():
                quantity = int(quantity)
                total_value = Decimal(str(total_value))
                
                if quantity <= 0:
                    return []
                
                unit_value = (total_value / quantity).quantize(Decimal('0.01'))
                
                created_sales = []
                for i in range(quantity):
                    # For the last one, we might need to adjust for rounding to match total_value exactly
                    # but for simplicity and since user said "divide cost by count", equal split is fine.
                    # If they want exact precision:
                    current_value = unit_value
                    if i == quantity - 1:
                        current_value = total_value - (unit_value * (quantity - 1))
                    
                    sale = Sale.create(
                        product=product,
                        total_value=current_value
                    )
                    created_sales.append(sale)
                
                # Adjust inventory once for the whole quantity
                product.adjust_inventory(-quantity)
                
                # Adjust filament inventory
                total_usage = product.total_filament_usage
                for filament, grams_per_unit in total_usage.items():
                    total_grams = grams_per_unit * quantity
                    filament.adjust_inventory(total_grams)
                    
                logger.info(f"Recorded sale of {quantity}x {product}")
                return created_sales
        except Exception as e:
            logger.error(f"Error creating sale: {e}")
            raise

    @staticmethod
    def calculate_printable_count(product):
        """
        Calculates how many of a given product could be printed with current filament inventory.
        """
        try:
            total_usage = product.total_filament_usage
            if not total_usage:
                return 0
            
            limit = None
            for filament, grams_needed in total_usage.items():
                if grams_needed <= 0:
                    continue
                
                # Total grams available for this filament
                total_available = filament.grams_remaining + (filament.rolls_in_stock * filament.grams_per_roll)
                can_print = int(total_available // grams_needed)
                
                if limit is None or can_print < limit:
                    limit = can_print
            
            return limit if limit is not None else 0
        except Exception as e:
            logger.error(f"Error calculating printable count: {e}")
            return 0

    @staticmethod
    def get_active_sales():
        """
        Returns all sales ordered by date.
        """
        try:
            return Sale.select().order_by(Sale.date.desc())
        except Exception as e:
            logger.error(f"Error fetching active sales: {e}")
            return []

    @staticmethod
    def update_sale(sale_id, **data):
        """
        Updates a sale record and adjusts product inventory if needed.
        data: dict with product, total_value, date
        """
        try:
            with db.atomic():
                sale = Sale.get_by_id(sale_id)
                old_product = sale.product
                new_product = data.get('product', old_product)
                
                # If product changed, adjust inventory for both
                if old_product != new_product:
                    old_product.adjust_inventory(1) # Revert old
                    new_product.adjust_inventory(-1) # Apply new
                    
                    # Revert filament for old product
                    old_usage = old_product.total_filament_usage
                    for filament, grams in old_usage.items():
                        filament.adjust_inventory(-grams) # Negative to add back
                    
                    # Apply filament for new product
                    new_usage = new_product.total_filament_usage
                    for filament, grams in new_usage.items():
                        filament.adjust_inventory(grams) # Positive to subtract
                
                for key, value in data.items():
                    setattr(sale, key, value)
                sale.save()
                logger.info(f"Updated sale ID: {sale_id}")
                return sale
        except Exception as e:
            logger.error(f"Error updating sale {sale_id}: {e}")
            raise

    @staticmethod
    def delete_sale(sale_id):
        """
        Deletes a sale and reverts the product inventory.
        """
        try:
            with db.atomic():
                sale = Sale.get_by_id(sale_id)
                sale.product.adjust_inventory(1) # Revert inventory
                
                # Revert filament usage
                usage = sale.product.total_filament_usage
                for filament, grams in usage.items():
                    filament.adjust_inventory(-grams) # Add back
                    
                sale.delete_instance()
                logger.info(f"Deleted sale ID: {sale_id}")
                return True
        except Exception as e:
            logger.error(f"Error deleting sale {sale_id}: {e}")
            raise

    @staticmethod
    def get_analytics_data(start_date, end_date):
        """
        Aggregates sales data within a date range.
        start_date, end_date: datetime objects
        """
        sales = Sale.select().where(
            (Sale.date >= start_date) & 
            (Sale.date <= end_date)
        ).order_by(Sale.date)
        
        data = {
            'total_sales_count': len(sales),
            'gross_revenue': Decimal('0.00'),
            'total_cost': Decimal('0.00'),
            'net_profit': Decimal('0.00'),
            'product_breakdown': {}, # product_name: {count, revenue, cost}
            'filament_usage': {},    # filament_name: grams
            'daily_stats': {},       # date_str: {revenue, cost, profit}
        }
        
        for sale in sales:
            prod = sale.product
            data['gross_revenue'] += sale.total_value
            
            # Product breakdown
            prod_name = str(prod)
            if prod_name not in data['product_breakdown']:
                data['product_breakdown'][prod_name] = {
                    'count': 0,
                    'revenue': Decimal('0.00'),
                    'cost': Decimal('0.00')
                }
            data['product_breakdown'][prod_name]['count'] += 1
            data['product_breakdown'][prod_name]['revenue'] += sale.total_value
            
            # Calculate cost for this specific sale (at current material prices)
            sale_cost = prod.total_cost
            data['total_cost'] += sale_cost
            data['product_breakdown'][prod_name]['cost'] += sale_cost
            
            # Daily stats
            date_str = sale.date.strftime("%Y-%m-%d")
            if date_str not in data['daily_stats']:
                data['daily_stats'][date_str] = {
                    'revenue': Decimal('0.00'),
                    'cost': Decimal('0.00'),
                    'profit': Decimal('0.00')
                }
            data['daily_stats'][date_str]['revenue'] += sale.total_value
            data['daily_stats'][date_str]['cost'] += sale_cost
            data['daily_stats'][date_str]['profit'] += (sale.total_value - sale_cost)

            # Filament usage breakdown
            usage = prod.total_filament_usage
            for filament, grams in usage.items():
                fil_name = str(filament)
                if fil_name not in data['filament_usage']:
                    data['filament_usage'][fil_name] = {'grams': Decimal('0.00'), 'cost': Decimal('0.00')}
                
                data['filament_usage'][fil_name]['grams'] += grams
                
                # Calculate cost for this specific filament usage
                fil_cost = (grams / filament.grams_per_roll) * filament.cost_per_roll
                data['filament_usage'][fil_name]['cost'] += fil_cost
                
        data['net_profit'] = data['gross_revenue'] - data['total_cost']
        return data

    @staticmethod
    def get_todo_data():
        """
        Returns a dictionary with 'to_print' and 'to_order' lists.
        'to_print': List of top 4 products that sell most and have stock < 3.
        'to_order': List of filaments to order with quantities.
        """
        from peewee import fn
        # 1. Calculate sales count for each product
        sales_counts = (Sale
                        .select(Sale.product, fn.COUNT(Sale.id).alias('count'))
                        .group_by(Sale.product))
        
        count_map = {s.product_id: s.count for s in sales_counts}
        
        # 2. Get next 4 things to print
        # Products needing stock (less than 3)
        needing_stock = Product.select().where(Product.inventory_count < 3)
        
        # Sort needing_stock by sales count
        sorted_products = sorted(needing_stock, key=lambda p: count_map.get(p.id, 0), reverse=True)
        to_print = sorted_products[:4]
        
        # 3. Calculate filament to order
        # Requirement: print min 6 of any product + what the to_print list will consume
        
        all_filaments = Filament.select()
        to_order = []
        all_products = list(Product.select())
        
        for filament in all_filaments:
            # G_todo(F) = grams needed to reach stock of 3 for everything in to_print
            grams_todo = Decimal('0')
            for p in to_print:
                usage = p.total_filament_usage
                grams_needed_per_unit = usage.get(filament, Decimal('0'))
                units_needed = max(0, 3 - p.inventory_count)
                grams_todo += grams_needed_per_unit * Decimal(str(units_needed))
            
            # G_buffer(F) = max grams needed to print 6 of ANY single product
            max_grams_for_6 = Decimal('0')
            for p in all_products:
                usage = p.total_filament_usage
                grams_needed_per_unit = usage.get(filament, Decimal('0'))
                max_grams_for_6 = max(max_grams_for_6, grams_needed_per_unit * 6)
            
            total_needed = grams_todo + max_grams_for_6
            
            # G_available(F)
            total_available = filament.grams_remaining + (filament.rolls_in_stock * filament.grams_per_roll)
            
            grams_to_order = max(Decimal('0'), total_needed - total_available)
            
            if grams_to_order > 0:
                rolls_to_order = int((grams_to_order / filament.grams_per_roll).to_integral_value(rounding='ROUND_UP'))
                to_order.append({
                    'filament': filament,
                    'rolls': rolls_to_order,
                    'grams': grams_to_order
                })
        
        return {
            'to_print': to_print,
            'to_order': to_order
        }

class SaleDraft:
    """
    A helper class for the GUI to manage a sale in memory before 
    committing it to the database.
    """
    def __init__(self):
        self.product = None
        self.quantity = 1
        self.total_value = Decimal('0.00')

    def set_data(self, product, quantity, total_value):
        self.product = product
        self.quantity = quantity
        self.total_value = Decimal(str(total_value))

    def save(self):
        """Commits the draft to the database using the service."""
        if not self.product:
            return None
        return InventoryService.create_sale(self.product, self.quantity, self.total_value)
