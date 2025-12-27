from models import Filament, Product, Part, db
from decimal import Decimal

def populate_etsy_products():
    """
    Populates the database with products based on the Etsy shop listings.
    """
    with db.atomic():
        # 1. Ensure filaments exist
        def get_filament(color, material="PLA", brand="Generic", cost=15.00):
            fil, _ = Filament.get_or_create(
                brand=brand,
                material=material,
                color=color,
                defaults={
                    'cost_per_roll': Decimal(str(cost)),
                    'grams_per_roll': Decimal('1000'),
                    'grams_remaining': Decimal('1000'),
                    'rolls_in_stock': 1
                }
            )
            return fil

        black = get_filament("Black Matte", cost=14.28)
        pink = get_filament("Pink Matte", cost=15.00)
        marble = get_filament("Marble")
        bone = get_filament("Bone")
        white = get_filament("White")
        red = get_filament("Red")
        vlad_red = get_filament("Vlad Red", cost=18.00) # Assuming specialty filament

        # 2. Helper for scaling
        # XL is 100%, L is 75%, M is 50%, S is 25% (roughly)
        size_scales = {
            "XL": Decimal('1.0'),
            "Large": Decimal('0.75'),
            "Medium": Decimal('0.5'),
            "Small": Decimal('0.25'),
            "Standard": Decimal('1.0')
        }

        # --- Product 1: Gothic Gargoyle Hygrometer/Thermometer ---
        if not Product.select().where(Product.product_type == "Gothic Gargoyle Hygrometer").exists():
            gargoyle = Product.create(
                product_type="Gothic Gargoyle Hygrometer",
                size="Standard",
                color_variant="Grey/Stone",
                inventory_count=2
            )
            # Approximating gargoyle: ~150g, 8h print
            part = gargoyle.add_part("Gargoyle Body", print_time_hours=8.0)
            part.add_filament_usage(marble, 150)
            print("Added Gothic Gargoyle Hygrometer")

        # --- Product 2: Gothic Snake Hide ---
        gothic_styles = {
            "Black": [(black, 1.0)],
            "Pink": [(pink, 1.0)],
            "Marble + bone skull": [(marble, 0.9), (bone, 0.1)],
            "Black/Pink": [(black, 0.85), (pink, 0.15)],
            "White/blood": [(white, 0.9), (red, 0.1)],
            "Vlad": [(vlad_red, 0.7), (black, 0.3)]
        }
        
        # Baseline from seed_data (XL Black/Pink)
        # Total Black: 530.55g, Total Pink: 100.98g, Total Time: 22.2h
        # Total weight: ~631.5g
        
        for size in ["Small", "Medium", "Large", "XL"]:
            scale = size_scales[size]
            for style, filament_mix in gothic_styles.items():
                if not Product.select().where(
                    (Product.product_type == "Gothic snake hide") & 
                    (Product.size == size) & 
                    (Product.color_variant == style)
                ).exists():
                    p = Product.create(
                        product_type="Gothic snake hide",
                        size=size,
                        color_variant=style,
                        inventory_count=0
                    )
                    
                    # Total time and weight scaled
                    total_time = Decimal('22.2') * scale
                    total_weight = Decimal('631.5') * scale
                    
                    # We split into parts like the reference: Lid (43%), Base (50%), Skull (7%)
                    # Lid
                    lid = p.add_part("Lid", print_time_hours=(total_time * Decimal('0.43')).quantize(Decimal('0.01')))
                    # Base
                    base = p.add_part("Base", print_time_hours=(total_time * Decimal('0.50')).quantize(Decimal('0.01')))
                    # Skull
                    skull = p.add_part("Skull", print_time_hours=(total_time * Decimal('0.07')).quantize(Decimal('0.01')))
                    
                    # Apply filaments based on mix
                    for fil, ratio in filament_mix:
                        lid.add_filament_usage(fil, (total_weight * Decimal('0.43') * Decimal(str(ratio))).quantize(Decimal('0.01')))
                        base.add_filament_usage(fil, (total_weight * Decimal('0.50') * Decimal(str(ratio))).quantize(Decimal('0.01')))
                        # Skull usually the accent color if it exists
                        skull_ratio = Decimal(str(ratio))
                        if len(filament_mix) > 1 and fil == filament_mix[1][0]:
                            # Accent color takes more of the skull
                             skull.add_filament_usage(fil, (total_weight * Decimal('0.07')).quantize(Decimal('0.01')))
                        elif len(filament_mix) == 1:
                             skull.add_filament_usage(fil, (total_weight * Decimal('0.07')).quantize(Decimal('0.01')))

            print(f"Added Gothic snake hide variations for size {size}")

        # --- Product 3: Strawberry Snake Hide ---
        strawberry_variants = {
            "Red": [(red, 0.9), (white, 0.1)], # Red with white seeds/parts
            "Pink": [(pink, 0.9), (white, 0.1)]
        }
        # Approximate Strawberry: Large is ~400g, 15h
        for size in ["Small", "Medium", "Large"]:
            scale = size_scales[size]
            for color, mix in strawberry_variants.items():
                if not Product.select().where(
                    (Product.product_type == "Strawberry snake hide") & 
                    (Product.size == size) & 
                    (Product.color_variant == color)
                ).exists():
                    p = Product.create(
                        product_type="Strawberry snake hide",
                        size=size,
                        color_variant=color,
                        inventory_count=0
                    )
                    total_time = Decimal('15.0') * scale
                    total_weight = Decimal('400.0') * scale
                    
                    # Parts: Fruit (80%), Stem (20%)
                    fruit = p.add_part("Fruit Body", print_time_hours=(total_time * Decimal('0.8')).quantize(Decimal('0.01')))
                    stem = p.add_part("Stem/Seeds", print_time_hours=(total_time * Decimal('0.2')).quantize(Decimal('0.01')))
                    
                    for fil, ratio in mix:
                        fruit.add_filament_usage(fil, (total_weight * Decimal('0.8') * Decimal(str(ratio))).quantize(Decimal('0.01')))
                        stem.add_filament_usage(fil, (total_weight * Decimal('0.2') * Decimal(str(ratio))).quantize(Decimal('0.01')))
            print(f"Added Strawberry snake hide variations for size {size}")

        # --- Product 4: Coffin Snake Hide - Flat Top ---
        coffin_styles = {
            "Black": [(black, 1.0)],
            "Black/Pink": [(black, 0.8), (pink, 0.2)]
        }
        # Approximate Coffin: Large is ~500g, 18h
        for size in ["Small", "Large"]:
            scale = size_scales[size]
            for style, mix in coffin_styles.items():
                if not Product.select().where(
                    (Product.product_type == "Coffin snake hide") & 
                    (Product.size == size) & 
                    (Product.color_variant == style)
                ).exists():
                    p = Product.create(
                        product_type="Coffin snake hide",
                        size=size,
                        color_variant=style,
                        inventory_count=0
                    )
                    total_time = Decimal('18.0') * scale
                    total_weight = Decimal('500.0') * scale
                    
                    # Parts: Coffin Base (60%), Coffin Lid (40%)
                    c_base = p.add_part("Coffin Base", print_time_hours=(total_time * Decimal('0.6')).quantize(Decimal('0.01')))
                    c_lid = p.add_part("Coffin Lid", print_time_hours=(total_time * Decimal('0.4')).quantize(Decimal('0.01')))
                    
                    for fil, ratio in mix:
                        c_base.add_filament_usage(fil, (total_weight * Decimal('0.6') * Decimal(str(ratio))).quantize(Decimal('0.01')))
                        c_lid.add_filament_usage(fil, (total_weight * Decimal('0.4') * Decimal(str(ratio))).quantize(Decimal('0.01')))
            print(f"Added Coffin snake hide variations for size {size}")

if __name__ == "__main__":
    import os
    import sys
    # Add parent directory to path to allow importing models
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from database import initialize_database
    initialize_database()
    db.connect(reuse_if_open=True)
    populate_etsy_products()
    db.close()
