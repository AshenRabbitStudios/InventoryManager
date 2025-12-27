import os

# Project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database paths
DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'inventory_manager.db')
TEST_DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'test_inventory_manager.db')

# Ensure data directory exists
os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)