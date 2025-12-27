from peewee import SqliteDatabase, Model, Proxy
import os
from config import DATABASE_PATH, TEST_DATABASE_PATH

# Use Proxy to allow dynamic database switching
db = Proxy()

def set_database(env_name):
    """Sets the database based on environment name ('prod' or 'test')"""
    pragmas = {
        'journal_mode': 'wal',
        'cache_size': -1024 * 64,  # 64MB
        'foreign_keys': 1,
        'ignore_check_constraints': 0,
    }
    if env_name == 'test':
        actual_db = SqliteDatabase(TEST_DATABASE_PATH, pragmas=pragmas)
    else:
        actual_db = SqliteDatabase(DATABASE_PATH, pragmas=pragmas)
    db.initialize(actual_db)

# Initialize with default or environment variable
initial_env = os.environ.get('INVENTORYMANAGER_ENV', 'prod')
set_database(initial_env)

class BaseModel(Model):
    class Meta:
        database = db