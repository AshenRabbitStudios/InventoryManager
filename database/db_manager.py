from models import db, Filament, FilamentPurchase, Product, Part, ProductFilament, PartFilament, Sale, SaleItem

def initialize_database():
    """Create all tables if they don't exist"""
    db.connect()
    db.create_tables([Filament, FilamentPurchase, Product, Part, ProductFilament, PartFilament, Sale, SaleItem])
    print("Database initialized successfully!")
    db.close()

def reset_database():
    """Drop and recreate all tables (USE WITH CAUTION)"""
    db.connect()
    # Explicitly list tables to drop, but use models if possible.
    # To be safe and clean, we'll try to drop all tables in the DB.
    all_tables = db.get_tables()
    db.execute_sql('PRAGMA foreign_keys = OFF;')
    for table in all_tables:
        db.execute_sql(f'DROP TABLE IF EXISTS "{table}";')
    db.execute_sql('PRAGMA foreign_keys = ON;')
    
    db.create_tables([Filament, FilamentPurchase, Product, Part, ProductFilament, PartFilament, Sale, SaleItem])
    print("Database reset complete!")
    db.close()