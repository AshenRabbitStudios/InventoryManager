from models import Filament, Product, Part, PartFilament, Sale, db
from decimal import Decimal
from datetime import datetime, timedelta
import random

def seed_example_data():
    """
    Seeds the database with the Gothic hide example and some sales if it doesn't already exist.
    Also calls the Etsy products population script.
    """
    # 1. Populate Etsy products first
    from .populate_etsy_products import populate_etsy_products
    populate_etsy_products()

    # Use a transaction to ensure atomicity
    with db.atomic():
        # 1. Create/Get Filaments
        black_pla, created_black = Filament.get_or_create(
            brand="Generic",
            material="PLA",
            color="Black Matte",
            defaults={
                'cost_per_roll': Decimal('14.28'),
                'grams_per_roll': Decimal('1000'),
                'grams_remaining': Decimal('1000'),
                'rolls_in_stock': 2
            }
        )
        
        pink_pla, created_pink = Filament.get_or_create(
            brand="Generic",
            material="PLA",
            color="Pink Matte",
            defaults={
                'cost_per_roll': Decimal('15.00'),
                'grams_per_roll': Decimal('1000'),
                'grams_remaining': Decimal('1000'),
                'rolls_in_stock': 2
            }
        )

        # 2. Check if the product already exists
        product_query = Product.select().where(
            (Product.product_type == "Gothic hide") & 
            (Product.size == "XL") & 
            (Product.color_variant == "Black/Pink")
        )
        
        if not product_query.exists():
            product = Product.create(
                product_type="Gothic hide",
                size="XL",
                color_variant="Black/Pink",
                inventory_count=5
            )
            
            # Lid: 161.67g black, 29.51g pink, 9h37m (~9.62h)
            lid = product.add_part("Lid", print_time_hours=9.62)
            lid.add_filament_usage(black_pla, 161.67)
            lid.add_filament_usage(pink_pla, 29.51)

            # Base: 368.88g black, 37.57g pink, 11h
            base = product.add_part("Base", print_time_hours=11.00)
            base.add_filament_usage(black_pla, 368.88)
            base.add_filament_usage(pink_pla, 37.57)

            # Skull: 33.9g pink, 1h 35m (~1.58h)
            skull = product.add_part("Skull", print_time_hours=1.58)
            skull.add_filament_usage(pink_pla, 33.9)
            
            print("Seeded Gothic hide example data successfully.")
        else:
            product = product_query.get()
            print("Gothic hide example data already exists.")

        # 3. Seed some sales if none exist
        if Sale.select().count() == 0:
            print("Seeding example sales...")
            base_price = Decimal('45.00')
            # Create sales over the last 30 days
            for i in range(20):
                days_ago = random.randint(0, 30)
                sale_date = datetime.now() - timedelta(days=days_ago)
                # Randomize price slightly
                price = base_price + Decimal(str(random.uniform(-5, 10))).quantize(Decimal('0.01'))
                
                Sale.create(
                    product=product,
                    total_value=price,
                    date=sale_date
                )
            print(f"Seeded 20 sales for {product}.")

if __name__ == "__main__":
    from database import initialize_database
    initialize_database()
    db.connect(reuse_if_open=True)
    seed_example_data()
    db.close()
